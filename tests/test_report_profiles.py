"""Reports must describe observed environments without carrying over native claims."""
import pytest


@pytest.mark.parametrize('verified', [False, True])
def test_docker_report_does_not_claim_windows_execution(monkeypatch, tmp_path, verified):
    import report
    import api.evidence as evidence
    folder = tmp_path / 'docs'
    folder.mkdir()
    for name in ['arquitetura.md', 'simuladores.md', 'riscos_residuais.md', 'questoes_dissertativas.md']:
        (folder / name).write_text('# Test-only template\nTemplate for unit test.\n', encoding='utf-8')
    # Synthetic input is used only in this temporary unit-test folder, never published as evidence.
    sample = {'environment': 'Docker Compose / unit fixture', 'exit_code': 0,
              'tests': [{'id': 'ENV-01', 'result': 'PASS', 'objective': 'unit fixture'}] if verified else []}
    monkeypatch.setattr(report, 'ROOT', tmp_path)
    monkeypatch.setattr(evidence, 'control_results', lambda: ([], sample))
    text = report.generate_sources()
    assert 'A suíte foi registrada no perfil Docker Compose' in text
    assert 'O Docker Desktop instalado falhou' not in text
    assert 'Os comandos descrevem o fluxo portátil' in text
    assert ('ENV-01 registrou os contêineres' in text) == verified
    assert ('ENV-01 não foi comprovado' in text) != verified
