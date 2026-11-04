import { existsSync } from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export function supportedNode(version) {
  const [major, minor] = version.split('.').map(Number);
  return major > 22 || (major === 22 && minor >= 12);
}

export function pythonCandidates(directory, platform = process.platform) {
  const envPython = path.join(directory, '.venv', platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  return [[envPython], ...(platform === 'win32' ? [['py', '-3.12'], ['python'], ['python3']] : [['python3.12'], ['python3'], ['python']])];
}

export function findPython(directory, platform = process.platform, probe = spawnSync) {
  const check = 'import sys,struct; sys.exit(0 if sys.version_info[:2]==(3,12) and struct.calcsize("P")==8 else 1)';
  return pythonCandidates(directory, platform).find(([command, ...args]) =>
    probe(command, [...args, '-c', check], {cwd: directory, stdio: 'ignore', windowsHide: true, timeout: 10000}).status === 0);
}

export function main() {
  if (!supportedNode(process.versions.node)) {
    console.error('Auto Repair precisa de Node.js 22.12 ou superior. Atualize o Node.js e execute npm start novamente.');
    process.exitCode = 1;
    return;
  }
  const python = findPython(root);
  if (!python) {
    console.error('Auto Repair precisa de Python 3.12 de 64 bits.');
    console.error(process.platform === 'win32'
      ? 'Instale: winget install --exact --id Python.Python.3.12\nDepois reabra o terminal e execute npm start.'
      : 'Instale Python 3.12 de 64 bits e execute npm start novamente.');
    process.exitCode = 1;
    return;
  }
  const npmCLI = process.env.npm_execpath || path.join(path.dirname(process.execPath), 'node_modules/npm/bin/npm-cli.js');
  if (!existsSync(npmCLI)) {
    console.error('Inicie pelo comando npm start para localizar o instalador do front.');
    process.exitCode = 1;
    return;
  }
  const [command, ...args] = python;
  const child = spawn(command, [...args, path.join(root, 'scripts/start_local.py'), ...process.argv.slice(2)], {
    cwd: root, stdio: 'inherit', env: {...process.env, AUTOBUDGET_NODE_EXEC: process.execPath, AUTOBUDGET_NPM_CLI: npmCLI}
  });
  child.on('error', error => { console.error(`Não foi possível iniciar o Python: ${error.message}`); process.exitCode = 1; });
  child.on('exit', code => { process.exitCode = code ?? 1; });
  // Both processes receive Ctrl+C from the terminal; let Python close its socket.
  process.on('SIGINT', () => {});
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
