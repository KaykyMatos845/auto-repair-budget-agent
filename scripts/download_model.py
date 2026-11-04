"""One-time, explicit download of pinned weights; inference never downloads files."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    manifest = json.loads((ROOT / 'model_manifest.json').read_text())
    target_dir = Path(os.environ.get('LOCAL_MODEL_DIR', ROOT / 'models'))
    created = not target_dir.exists()
    target_dir.mkdir(parents=True, exist_ok=True)
    if created:
        # Public model files may also be read by an unprivileged Docker user.
        target_dir.chmod(0o755)
    target = target_dir / manifest['filename']
    if target.is_file() and digest(target) == manifest['sha256']:
        print('Modelo já instalado e SHA-256 verificado.')
        return
    url = 'https://huggingface.co/{repository}/resolve/{revision}/{filename}'.format(**manifest)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target_dir, delete=False) as output:
            temporary = Path(output.name)
            with urllib.request.urlopen(url, timeout=120) as response:
                count = 0
                while chunk := response.read(1024 * 1024):
                    count += len(chunk)
                    if count > manifest['size']:
                        raise ValueError('O arquivo excede o tamanho esperado.')
                    output.write(chunk)
        if temporary.stat().st_size != manifest['size'] or digest(temporary) != manifest['sha256']:
            raise ValueError('Falha de integridade: tamanho ou SHA-256 diferente do manifesto.')
        temporary.chmod(0o644)
        temporary.replace(target)
        print('Modelo local instalado: 10,6 MB; SHA-256 verificado. Licença: ' + manifest['license'])
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Não foi possível instalar o modelo: ' + str(error), file=sys.stderr)
        sys.exit(1)
