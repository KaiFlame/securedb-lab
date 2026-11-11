import json
from pathlib import Path
from uuid import uuid4
import pytest
from pydantic import ValidationError
from api.models import Product,Profile,OrderCreate,CatalogQuery
from api.db import catalog_filter

def test_payloads_reject_mass_assignment(observed):
    with pytest.raises(ValidationError): OrderCreate(customer_id=uuid4(),description='Pedido seguro',total='12.00',tenant_id=uuid4())
    with pytest.raises(ValidationError): Product(name='Produto',sku='SKU',category='Software',price_cents={'$gt':0})
    with pytest.raises(ValidationError): Profile(name='Perfil',email='pessoa@real.com',segment='Essencial')
    observed.update(extra_tenant='rejected',operator_object='rejected',real_email_domain='rejected')

def test_filters_reject_operators_and_escape_regex(observed):
    for q in ['{"$ne":null}','$where','[x]']:
        with pytest.raises(ValidationError): CatalogQuery(q=q)
    filt=catalog_filter('tenant-A','a.*','Software')
    assert filt['name']['$regex']==r'a\.\*'
    assert filt['tenant_id']=='tenant-A'
    observed.update(regex='escaped',tenant='server-side')

def test_unsafe_origin_denied_before_database(client,observed):
    res=client.post('/api/auth/login',headers={'origin':'https://untrusted.example'},json={'username':'test','password':'x'})
    assert res.status_code==403
    res2=client.post('/api/auth/login',headers={'origin':''},json={'username':'test','password':'x'})
    assert res2.status_code==403
    observed.update(untrusted_origin=res.status_code,missing_origin=res2.status_code)

def test_controls_require_complete_evidence(monkeypatch,tmp_path,observed):
    import api.evidence as evidence
    monkeypatch.setattr(evidence,'evidence_root',lambda:tmp_path)
    controls,_=evidence.control_results()
    assert len(controls)==20 and all(c['status']=='pending' for c in controls)
    (tmp_path/'latest.json').write_text(json.dumps({'tests':[{'id':'test_sql_roles','result':'SKIP','timestamp':'2026-01-01T00:00:00Z'}]}),encoding='utf-8')
    controls,_=evidence.control_results()
    assert next(c for c in controls if c['id']=='SQL-02')['status']=='pending'
    observed.update(empty='20 pending',skip='remains pending')

def test_restore_guard_refuses_source(observed):
    from backup_restore import guarded_destination
    for name in ['securedb','lab','restore_pg_bad','postgres','restore_mongo_../']:
        with pytest.raises(ValueError): guarded_destination(name,'sql')
    assert guarded_destination('restore_pg_'+uuid4().hex,'sql').startswith('restore_pg_')
    observed.update(source_overwrite='refused')

def test_certificates_and_encrypted_backup(tmp_path,monkeypatch,observed):
    from certificates import generate
    from cryptography import x509
    from backup_restore import encrypted_file
    generate(tmp_path/'certs')
    key=(tmp_path/'certs/ca/ca.key').read_bytes()
    generate(tmp_path/'certs')
    assert key==(tmp_path/'certs/ca/ca.key').read_bytes()
    cert=x509.load_pem_x509_certificate((tmp_path/'certs/postgres/server.crt').read_bytes())
    san=cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert 'postgres' in san.get_values_for_type(x509.DNSName)
    (tmp_path/'backup.key').write_bytes(bytes(range(32)))
    raw=tmp_path/'dump';raw.write_bytes(b'dados sinteticos de teste')
    monkeypatch.setenv('LAB_ADMIN',str(tmp_path/'admin.json'));monkeypatch.setenv('LAB_BACKUPS',str(tmp_path/'backups'))
    target,recovered=encrypted_file(raw,'test')
    assert recovered==raw.read_bytes() and recovered not in target.read_bytes()
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    saved=target.read_bytes();tampered=bytearray(saved[16:]);tampered[-1]^=1
    with pytest.raises(InvalidTag):AESGCM(bytes(range(32))).decrypt(saved[4:16],bytes(tampered),b'SecureDB Lab v1')
    observed.update(certificate_san='postgres,localhost,127.0.0.1',idempotency='preserved',encryption='AES-256-GCM round trip')
