"""Prepare this checkout once, then always run its own Python environment."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]
ENV_DIR = ROOT / '.venv'
ENV_PYTHON = ENV_DIR / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
CACHE = ROOT / '.autobudget-local.json'
sys.path.insert(0, str(ROOT))


def dependency_report():
    from local_vision import dependency_issues
    issues = list(dependency_issues())
    for line in (ROOT / 'requirements.txt').read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        name, expected = line.strip().split('==')
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            actual = None
        if actual != expected:
            issues.append({'module': name, 'kind': 'version' if actual else 'missing',
                           'detail': f'Esperado {expected}; instalado {actual or "nenhum"}.'})
    return {'python': sys.executable, 'issues': issues}


def run(command):
    subprocess.run([str(item) for item in command], cwd=ROOT, check=True)


def probe_dependencies():
    result = subprocess.run([str(ENV_PYTHON), str(Path(__file__)), '--dependency-report'],
                            cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Falha ao verificar o ambiente Python: ' + result.stderr.strip())
    return json.loads(result.stdout)


def describe_issues(issues):
    for issue in issues:
        print(f"  {issue['module']}: {issue['detail']}", flush=True)
    if os.name == 'nt' and any('dll' in issue['detail'].lower() for issue in issues):
        print('Falha de DLL no Windows: confira o Microsoft Visual C++ Runtime x64.\n'
              'Instalador oficial: https://aka.ms/vs/17/release/vc_redist.x64.exe', flush=True)


def frontend_fingerprint():
    files = [ROOT / name for name in ['index.html', 'vite.config.js', 'package.json', 'package-lock.json']]
    for directory in ['src', 'public']:
        files.extend(path for path in (ROOT / directory).rglob('*') if path.is_file())
    digest = hashlib.sha256()
    for path in sorted(files):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(b'\0')
        digest.update(path.read_bytes())
    return digest.hexdigest()


def prepare_frontend():
    try:
        cached = json.loads(CACHE.read_text())
    except (OSError, ValueError):
        cached = {}
    node, npm = os.environ['AUTOBUDGET_NODE_EXEC'], os.environ['AUTOBUDGET_NPM_CLI']
    lock_hash = hashlib.sha256((ROOT / 'package-lock.json').read_bytes()).hexdigest()
    if cached.get('packages') != lock_hash or not (ROOT / 'node_modules/.package-lock.json').is_file():
        print('Preparando pacotes do front (precisa de internet nesta etapa)...', flush=True)
        run([node, npm, 'ci'])
        cached = {'packages': lock_hash}
        CACHE.write_text(json.dumps(cached))
    source_hash = frontend_fingerprint()
    if cached.get('build') != source_hash or not (ROOT / 'dist/index.html').is_file():
        print('Gerando a interface atualizada...', flush=True)
        run([node, npm, 'run', 'build'])
        cached['build'] = source_hash
        CACHE.write_text(json.dumps(cached))


def main(check=False, backend_only=False):
    os.chdir(ROOT)
    if Path(sys.prefix).resolve() != ENV_DIR.resolve():
        if check:
            print('O ambiente .venv ainda não está pronto. Execute npm start.', flush=True)
            return 1
        if not ENV_PYTHON.exists():
            print('Criando o ambiente Python exclusivo deste projeto...', flush=True)
            venv.EnvBuilder(with_pip=True).create(ENV_DIR)
        version = subprocess.run([str(ENV_PYTHON), '-c',
                                  'import sys,struct; sys.exit(0 if sys.version_info[:2]==(3,12) and struct.calcsize("P")==8 else 1)'])
        if version.returncode:
            raise RuntimeError('A .venv existente é incompatível. Renomeie essa pasta e execute npm start novamente.')
        args = ['--backend-only'] if backend_only else []
        return subprocess.call([str(ENV_PYTHON), str(Path(__file__)), *args], cwd=ROOT)

    print(f'Python do projeto: {sys.executable}', flush=True)
    report = probe_dependencies()
    if check:
        describe_issues(report['issues'])
        if not report['issues']:
            import server  # Loads the same .env as normal startup.
            from local_vision import get_session, LocalVisionError
            try:
                get_session()
            except LocalVisionError as error:
                print(str(error), flush=True)
                return 1
            print('Bibliotecas e modelo prontos.', flush=True)
        return int(bool(report['issues']))
    if report['issues']:
        print('Preparando bibliotecas locais (precisa de internet nesta etapa)...', flush=True)
        describe_issues(report['issues'])
        command = [ENV_PYTHON, '-m', 'pip', 'install', '--only-binary=:all:', '-r', ROOT / 'requirements.txt']
        if any(issue['kind'] == 'load' for issue in report['issues']):
            command.append('--force-reinstall')
        run(command)
        report = probe_dependencies()
        if report['issues']:
            describe_issues(report['issues'])
            raise RuntimeError('As bibliotecas ainda não carregam. Resolva o erro acima antes de abrir a análise.')
        run([ENV_PYTHON, '-m', 'pip', 'check'])
    if not backend_only:
        prepare_frontend()
    import server  # Shares .env settings, including a custom LOCAL_MODEL_DIR.
    from scripts.download_model import main as prepare_model
    print('Conferindo os pesos do detector...', flush=True)
    prepare_model()
    print('Iniciando o servidor. Mantenha este terminal aberto.', flush=True)
    os.environ['LOCAL_PRELOAD'] = '1'
    os.execv(str(ENV_PYTHON), [str(ENV_PYTHON), '-u', str(ROOT / 'server.py')])


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--backend-only', action='store_true')
    parser.add_argument('--dependency-report', action='store_true', help=argparse.SUPPRESS)
    options = parser.parse_args()
    try:
        if options.dependency_report:
            print(json.dumps(dependency_report()))
            sys.exit(0)
        sys.exit(main(options.check, options.backend_only))
    except KeyboardInterrupt:
        sys.exit(0)
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print('Não foi possível iniciar: ' + str(error), file=sys.stderr)
        sys.exit(1)
