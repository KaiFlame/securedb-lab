"""Local didactic CA. No downloaded certificates or verification bypasses."""
import ipaddress
from datetime import datetime, timedelta, timezone
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

def private_bytes(key):
    return key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption())

def generate(root):
    root = Path(root)
    expected = [root/'ca/ca.key', root/'ca/ca.crt', root/'client/ca.crt', root/'postgres/server.key', root/'postgres/server.crt', root/'mongo/server.pem']
    if all(p.exists() for p in expected):
        cert = x509.load_pem_x509_certificate((root/'ca/ca.crt').read_bytes())
        if cert.not_valid_after_utc <= datetime.now(timezone.utc):
            raise RuntimeError("CA expirada. Preserve os artefatos e gere uma nova pasta de certificados.")
        return
    if any(p.exists() for p in expected):
        raise RuntimeError("Certificados parciais; não sobrescrever chaves existentes. Verifique .local/certs.")
    for name in ['ca','client','postgres','mongo']:
        (root/name).mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    key = rsa.generate_private_key(public_exponent=65537,key_size=3072)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'SecureDB Lab - CA didática')])
    ca = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
          .serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=5)).not_valid_after(now+timedelta(days=90))
          .add_extension(x509.BasicConstraints(ca=True,path_length=0),critical=True)
          .add_extension(x509.KeyUsage(True,False,False,False,False,True,True,None,None),critical=True)
          .sign(key,hashes.SHA256()))
    ca_bytes=ca.public_bytes(serialization.Encoding.PEM)
    (root/'ca/ca.key').write_bytes(private_bytes(key))
    (root/'ca/ca.crt').write_bytes(ca_bytes)
    (root/'client/ca.crt').write_bytes(ca_bytes)
    for service in ['postgres','mongo']:
        server_key=rsa.generate_private_key(public_exponent=65537,key_size=3072)
        cert=(x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,service)]))
            .issuer_name(ca.subject).public_key(server_key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now-timedelta(minutes=5)).not_valid_after(now+timedelta(days=90))
            .add_extension(x509.BasicConstraints(ca=False,path_length=None),critical=True)
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(service),x509.DNSName('localhost'),x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]),critical=False)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),critical=False)
            .sign(key,hashes.SHA256()))
        server_bytes=cert.public_bytes(serialization.Encoding.PEM)
        (root/service/'server.crt').write_bytes(server_bytes)
        (root/service/'server.key').write_bytes(private_bytes(server_key))
        if service=='mongo':
            (root/service/'server.pem').write_bytes(private_bytes(server_key)+server_bytes)
            (root/service/'ca.crt').write_bytes(ca_bytes)
    for path in root.rglob('*'):
        if path.is_file() and path.suffix in {'.key','.pem'}:
            path.chmod(0o600)
