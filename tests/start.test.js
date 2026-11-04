import { test } from 'node:test';
import assert from 'node:assert/strict';
import { findPython, pythonCandidates } from '../scripts/start.mjs';

test('Windows prefers the project environment and passes paths with spaces without a shell', () => {
  const directory = 'C:/Users/Kayky Matos/AutoBudget';
  const calls = [];
  const python = findPython(directory, 'win32', (command, args, options) => {
    calls.push({command, args, options});
    return {status: 0};
  });
  assert.deepEqual(python, pythonCandidates(directory, 'win32')[0]);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].options.shell, undefined);
  assert.equal(calls[0].options.cwd, directory);
  assert.ok(calls[0].args.at(-1).includes('struct.calcsize("P")==8'));
});

test('missing or incompatible venv falls back to the Python 3.12 Windows launcher', () => {
  const calls = [];
  const python = findPython('/project', 'win32', (command, args) => {
    calls.push([command, ...args]);
    return {status: command === 'py' ? 0 : 1};
  });
  assert.deepEqual(python, ['py', '-3.12']);
  assert.equal(calls[1][1], '-3.12');
});

test('failed candidates never launch an incompatible interpreter', () => {
  assert.equal(findPython('/project', 'win32', () => ({status: null, error: new Error('not found')})), undefined);
  assert.equal(findPython('/project', 'linux', () => ({status: 1})), undefined);
});
