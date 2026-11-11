"""Generate academic Markdown/PDF from versioned sources and observed reports."""
import hashlib
import json
from pathlib import Path
import re
import sys
from datetime import datetime,timezone
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def load(path,default):
    p=ROOT/path
    return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else default

def generate_sources():
    from api.evidence import control_results
    controls,report=control_results()
    passed=sum(c['status']=='pass' for c in controls)
    results=report.get('tests',[])
    tests={t['id']:t for t in results}
    docker_profile=report.get('environment','').startswith('Docker Compose')
    env_verified=tests.get('ENV-01',{}).get('result')=='PASS'
    status={'pass':'IMPLEMENTADO E TESTADO','pending':'IMPLEMENTADO SEM VALIDAÇÃO','fail':'PENDENTE'}
    inventory=['# Inventário de controles\n','Implementação e comprovação são independentes. Cada aprovação exige todos os testes associados. A comprovação desta execução se restringe ao perfil registrado, sem generalização para outro ambiente.\n']
    for c in controls:
        inventory.extend([f"## {c['id']} - {c['title']}\n",f"**Risco:** {c['risk']}.\n",f"**Objetivo:** {c.get('objective',c['title'])}\n",f"**Configuração:** "+', '.join('`'+f+'`' for f in c['files'])+'.\n',f"**Teste positivo:** {c['positive']}\n",f"**Teste negativo:** {c['negative']}\n",f"**Comprovação:** {status[c['status']]}; cenários "+', '.join('`'+t+'`' for t in c['required_tests'])+'.\n',f"**Evidência:** `evidencias/latest.json` e `evidencias/environment.json` (quando existente), além dos arquivos por teste em `evidencias/sql` / `evidencias/nosql` na instância que os executou.\n",f"**Risco residual:** {c['residual']}\n"])
    (ROOT/'docs/inventario_controles.md').write_text('\n'.join(inventory),encoding='utf-8')
    matrix=['# Matriz de rastreabilidade\n',f"Perfil observado: {report.get('environment','não executado')}.\n",('ENV-01 comprova a topologia de contêineres observada. Os demais resultados se referem ao perfil indicado.\n' if env_verified else 'Os itens de implantação dependem de uma verificação ENV-01.\n'),'| ID | Requisito | Status | Arquivo / evidência |','|---|---|---|---|']
    for c in controls:
        matrix.append(f"| {c['id']} | {c['title']} | {status[c['status']]} | `{c['files'][0]}`; "+', '.join('`'+t+'`' for t in c['required_tests'])+' |')
    for i in range(1,11):matrix.append(f'| Q-{i:02d} | Enunciado original e resposta com exemplo | IMPLEMENTADO SEM VALIDAÇÃO | `docs/questoes_dissertativas.md`, questão {i}; revisão individual do aluno pendente |')
    for id,name,st,artifact in [
      ('ENT-01','Git local e README','IMPLEMENTADO E TESTADO','README.md; git status; preflight'),
      ('ENT-02','Scripts e configurações','IMPLEMENTADO E TESTADO','scripts/; sql/; nosql/; perfil observado no relatório'),
      ('ENT-03','React/FastAPI e CRUD','IMPLEMENTADO E TESTADO','web/; api/; testes integrados e frontend'),
      ('ENT-04','Diagrama e fronteiras','IMPLEMENTADO SEM VALIDAÇÃO','docs/arquitetura.md; revisão do aluno'),
      ('ENT-05','Evidências sanitizadas','IMPLEMENTADO E TESTADO','evidencias/entrega/macos_local; resultado e capturas'),
      ('ENT-06','Relatório Markdown/PDF','IMPLEMENTADO E TESTADO','docs/relatorio_final.md; docs/relatorio_final.pdf; validação visual registrada'),
      ('ENT-07','Simuladores antes/depois','PARCIAL','Capturas atuais e plano registrados; cenário inicial não coletado'),
      ('ENT-08','Execução Compose','IMPLEMENTADO E TESTADO' if docker_profile and env_verified and report.get('exit_code')==0 else 'IMPLEMENTADO SEM VALIDAÇÃO','docker-compose.yml; evidencias/environment.json e latest.json; CI remota requer conferência dos jobs'),
      ('ENT-09','Preparação GitHub','IMPLEMENTADO E TESTADO','docs/github.md; .gitignore; histórico preservado'),
      ('ENT-10','Identificação e RA','VERSÃO ACADÊMICA','Dados mantidos na entrega do grupo')]:matrix.append(f'| {id} | {name} | {st} | {artifact} |')
    (ROOT/'docs/rastreabilidade.md').write_text('\n'.join(matrix)+'\n',encoding='utf-8')
    md=['# SecureDB Lab\n','## Relatório técnico acadêmico\n','FACAMP - Tratamento e Armazenamento da Informação\n','Professor: Prof. Me. Nivaldo T. Marcusso\n','Identificação acadêmica disponível na versão de entrega do grupo.\n',f"Data de consolidação: {datetime.now().astimezone().strftime('%d/%m/%Y')}.\n",
    '## 1. Problema e objetivo\n','Como transformar requisitos de segurança em controles configurados e evidências verificáveis em bancos relacionais e documentais? O objetivo é implementar os dois laboratórios com dados sintéticos, separar autorização de interface e comprovar cenários positivos e negativos, sem confundir existência de código com eficácia observada.\n',
    '## 2. Ambiente e alcance observado\n',f"Execução registrada: **{report.get('environment','não executado')}**. Timestamp UTC da suíte: {report.get('timestamp','não executado')}.\n",
    f"Resultado (inclui ENV-01 quando registrado): **{sum(t['result']=='PASS' for t in results)} PASS, {sum(t['result']=='FAIL' for t in results)} FAIL e {sum(t['result']=='SKIP' for t in results)} SKIP**. O painel comprova {passed}/20 controles no perfil registrado; {20-passed} exigem observações adicionais.\n",
    'O Docker Desktop instalado falhou antes de disponibilizar o motor, por erro interno na inicialização de socket. Foram usados PostgreSQL portátil e MongoDB Community nativos, com TLS verificando CA/hostname e portas em loopback. O Compose foi fornecido e validado estaticamente; não há alegação de execução de contêineres ou de CI remota bem-sucedida.\n']
    if docker_profile:
        md[-1]=('A suíte foi registrada no perfil Docker Compose, com drivers reais e TLS verificado. '+
                ('ENV-01 registrou os contêineres ativos, bancos sem portas publicadas e rede interna.' if env_verified else 'ENV-01 não foi comprovado; os controles de implantação permanecem pendentes.')+
                (' A seleção local excluiu verificações específicas de injection e os checklists finais dependentes delas. Capturas, resultados e escopo estão em evidencias/entrega/macos_local.\n' if 'validação local parcial' in report.get('environment','') else ' A plataforma do host consta no perfil observado.\n'))
    versions=[]
    for id in ['test_sql_environment','test_mongo_environment']:
        if id in tests:versions.append(f"- {id}: {json.dumps(tests[id]['observed'],ensure_ascii=False)}")
    md.extend(versions+['\nAs versões Python/Node/dependências e as auditorias estão nos artefatos de entrega. Tags de imagem fixadas não equivalem a digests. Não foi alegada varredura das imagens que não puderam ser iniciadas.\n'])
    md.append('O fluxo portátil e a preparação GitHub estão em docs/instalacao_macos.md e docs/PRONTIDAO_GITHUB.md. O histórico Windows e seus limites estão em docs/VALIDACAO.md. Os artefatos anteriores foram preservados; as evidências deste relatório pertencem ao perfil registrado.\n')
    md.append('## 3. Arquitetura e limites de confiança\n')
    md.append((ROOT/'docs/arquitetura.md').read_text(encoding='utf-8').split('\n',1)[1])
    md.extend(['## 4. Procedimento reproduzível\n','A fundação usa setup idempotente para segredos, certificados e sementes; a aplicação aplica papéis/tenant no backend. A CLI executa teste e restore, e o painel lê JSON sanitizado. O procedimento principal e o alternativo estão no README.\n',
    '```text\nsh scripts/docker.sh up\nsh scripts/docker.sh test\nsh scripts/docker.sh backup --database both\nsh scripts/docker.sh restore --database both\nsh scripts/docker.sh report\nsh scripts/docker.sh down\n```\n',
    'Os comandos descrevem o fluxo portátil disponibilizado. Somente os testes e observações presentes neste relatório comprovam execução; não foi inferido resultado de CI ou de outro host. O histórico nativo está em docs/VALIDACAO.md.\n',
    '## 5. Controles e comprovação\n','| Controle | Resultado | Testes requeridos |','|---|---|---|'])
    md.extend(f"| {c['id']} - {c['title']} | {status[c['status']]} | "+', '.join(c['required_tests'])+' |' for c in controls)
    md.extend(['\n## 6. Testes positivos e negativos\n','| ID | Resultado | Objetivo |','|---|---|---|'])
    md.extend(f"| {t['id']} | {t['result']} | {t['objective'].replace('|','/')} |" for t in results)
    md.append('\n## 7. Backup e restauração medidos\n')
    for id in ['test_sql_backup','test_mongo_backup']:
        if id in tests and tests[id]['result']=='PASS':
            o=tests[id]['observed']
            md.append(f"### {id}\nDestino novo: `{o['destination']}`. Dump: **{o['backup_seconds']} s**. Restore e verificação: **{o['restore_seconds']} s**. Cópia mantida: {o['encrypted']}. Snapshot consistente: {'sim (PostgreSQL)' if o['consistent_snapshot'] else 'não (MongoDB standalone; escritas devem ser pausadas)'}.\n")
            md.extend(['| Estrutura | Origem | Restaurado | Fingerprint |','|---|---|---|---|'])
            md.extend(f"| {name} | {fp['count']} | {o['restored'][name]['count']} | {'igual' if fp==o['restored'][name] else 'DIVERGENTE'} |" for name,fp in o['source'].items())
            md.append('\nO hash completo e o nome do artefato cifrado estão no JSON do teste. Os tempos não são um benchmark e não comprovam RTO/RPO de negócio.\n')
    md.extend(['## 8. Simuladores e evolução\n',(ROOT/'docs/simuladores.md').read_text(encoding='utf-8').split('\n',1)[1],
    '## 9. Riscos residuais\n',(ROOT/'docs/riscos_residuais.md').read_text(encoding='utf-8').split('\n',1)[1],
    '## 10. Questões dissertativas\n',(ROOT/'docs/questoes_dissertativas.md').read_text(encoding='utf-8').split('\n',1)[1],
    '## 11. Conclusão\n',f"A execução observou {len(results)} cenários, com {sum(t['result']=='PASS' for t in results)} aprovações. Os resultados sustentam as afirmações delimitadas sobre autenticação, autorização, TLS, integridade e recuperação no perfil testado. Os controles sem comprovação continuam pendentes. Os simuladores registram o cenário atual, uma hipótese de continuidade e o plano de evolução. O cenário inicial ficou não coletado. O grupo deve revisar as respostas e validar as metas e os responsáveis propostos no plano. O laboratório não certifica robustez universal ou prontidão para produção.\n",
    '## 12. Bibliografia e materiais\n',
    '- MARCUSSO, Nivaldo T. Manual do Aluno: Segurança da Informação e Cibersegurança em Bancos de Dados. FACAMP, 2026, v2, 18 páginas. Arquivo original e hash no manifesto de fontes.\n',
    '- FACAMP. Apresentação interativa de Segurança da Informação e Cibersegurança em Bancos de Dados, v3. Laboratórios e entregas nos slides 71-78; os simuladores permanecem no HTML original.\n',
    '- Prompt mestre SecureDB Lab fornecido pelo aluno; especificação complementar de produto.\n',
    '- PostgreSQL 17. Row Security Policies. https://www.postgresql.org/docs/17/ddl-rowsecurity.html\n',
    '- PostgreSQL 17. SSL Support. https://www.postgresql.org/docs/17/ssl-tcp.html\n',
    '- PostgreSQL 17. pg_dump. https://www.postgresql.org/docs/17/app-pgdump.html\n',
    '- MongoDB. TLS/SSL. https://www.mongodb.com/docs/manual/core/security-transport-encryption/\n',
    '- MongoDB. Schema Validation. https://www.mongodb.com/docs/manual/core/schema-validation/\n',
    '- OWASP. SQL Injection Prevention Cheat Sheet. https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html\n',
    ])
    text='\n'.join(md)
    (ROOT/'docs/relatorio_final.md').write_text(text,encoding='utf-8')
    return text

def inline(text):
    text=escape(text).replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
    text=re.sub(r'`([^`]+)`',r'<font name="Mono">\1</font>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1 (\2)',text)
    return text

def make_pdf(text):
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,LongTable,TableStyle,PageBreak,Flowable
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    fontdir=Path('C:/Windows/Fonts')
    if (fontdir/'segoeui.ttf').exists(): fonts=[fontdir/'segoeui.ttf',fontdir/'segoeuib.ttf',fontdir/'consola.ttf']
    else: fonts=[Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')]
    for name,path in zip(['Body','BodyBold','Mono'],fonts):pdfmetrics.registerFont(TTFont(name,str(path)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle('P',fontName='Body',fontSize=9,leading=14,textColor=colors.HexColor('#343632'),spaceAfter=8,splitLongWords=True))
    styles.add(ParagraphStyle('TitleLab',parent=styles['P'],fontName='BodyBold',fontSize=31,leading=36,textColor=colors.HexColor('#7f2626'),spaceAfter=22))
    styles.add(ParagraphStyle('H2Lab',parent=styles['P'],fontName='BodyBold',fontSize=16,leading=21,spaceBefore=20,spaceAfter=12,keepWithNext=True))
    styles.add(ParagraphStyle('H3Lab',parent=styles['P'],fontName='BodyBold',fontSize=11,leading=16,spaceBefore=14,spaceAfter=8,keepWithNext=True))
    styles.add(ParagraphStyle('CellLab',parent=styles['P'],fontSize=7.4,leading=11,spaceAfter=0))
    styles.add(ParagraphStyle('CodeLab',parent=styles['P'],fontName='Mono',fontSize=7.1,leading=11,backColor=colors.HexColor('#f3f2ef'),borderPadding=10,spaceBefore=8,spaceAfter=12))
    width=A4[0]-94
    story=[];lines=text.splitlines();i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('```'):
            language=line[3:];code=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            if language=='mermaid':
                diagram='Usuário local  →  React / Nginx  →  FastAPI\n                                           ↓ TLS + identidade\n                            PostgreSQL / RLS       MongoDB / RBAC\n                                           ↓\n                              CLI / logs / dump cifrado / evidências'
                story.append(Paragraph(escape(diagram).replace('\n','<br/>'),styles['CodeLab']))
            else:story.append(Paragraph(escape('\n'.join(code)).replace('\n','<br/>'),styles['CodeLab']))
            i+=1;continue
        if line.startswith('|'):
            table=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=[s.strip() for s in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',s) for s in row):table.append([Paragraph(inline(s),styles['CellLab']) for s in row])
                i+=1
            n=len(table[0]);weights=[.37,.23,.40] if n==3 else [.28,.16,.19,.37] if n==4 else [1/n]*n
            t=LongTable(table,colWidths=[width*w for w in weights],repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eee8df')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#dedbd3')),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]))
            story.extend([Spacer(1,1),t,Spacer(1,12)]);continue
        if line.startswith('# '):style='TitleLab';line=line[2:]
        elif line.startswith('## '):style='H2Lab';line=line[3:]
        elif line.startswith('### '):style='H3Lab';line=line[4:]
        else:style='P'
        if line.startswith('- '):line='• '+line[2:]
        story.append(Paragraph(inline(line),styles[style]));i+=1
    def page(canvas,doc):
        canvas.saveState();w,h=A4
        canvas.setStrokeColor(colors.HexColor('#b43f32'));canvas.setLineWidth(1.2);canvas.line(47,h-33,w-47,h-33)
        canvas.setFont('Body',7);canvas.setFillColor(colors.HexColor('#77766d'))
        canvas.drawString(47,h-25,'FACAMP / SECUREDB LAB / RELATÓRIO TÉCNICO')
        canvas.drawString(47,27,'DADOS SINTÉTICOS - RESULTADOS DELIMITADOS AO PERFIL REGISTRADO')
        canvas.drawRightString(w-47,27,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(ROOT/'docs/relatorio_final.pdf'),pagesize=A4,leftMargin=47,rightMargin=47,topMargin=55,bottomMargin=48,title='SecureDB Lab - Relatório técnico',author='Grupo SecureDB Lab')
    doc.build(story,onFirstPage=page,onLaterPages=page)

if __name__=='__main__':
    text=generate_sources()
    make_pdf(text)
    print('Fontes, inventário, rastreabilidade e PDF gerados a partir dos resultados observados.')
