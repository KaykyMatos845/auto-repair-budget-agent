import { test } from 'node:test';
import assert from 'node:assert/strict';
import { requestJson } from '../src/api.js';

test('API handles unavailable backends without exposing JSON parser errors', async t => {
  for (const [name, response, expected] of [
    ['empty Vite proxy error', new Response('', { status: 500 }), /resposta vazia \(HTTP 500\).*servidor Python/],
    ['HTML gateway error', new Response('<html>Bad gateway</html>', { status: 502 }), /resposta inválida \(HTTP 502\)/],
    ['truncated JSON', new Response('{"parts":', { status: 200 }), /resposta inválida/],
    ['null JSON', new Response('null'), /resposta inválida/],
    ['array JSON', new Response('[]'), /resposta inválida/],
    ['model error', Response.json({ error: 'Instale o modelo.', code: 'LOCAL_MODEL_MISSING' }, { status: 503 }), /Instale o modelo.*LOCAL_MODEL_MISSING/],
  ]) {
    await t.test(name, async t => {
      t.mock.method(globalThis, 'fetch', async () => response);
      await assert.rejects(requestJson('/api/analyze'), expected);
    });
  }
  await t.test('connection refused', async t => {
    t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('Failed to fetch'); });
    await assert.rejects(requestJson('/api/health'), /Não foi possível receber.*servidor Python/);
  });
  await t.test('valid analysis is passed through with request options', async t => {
    const data = { provider: 'local', parts: [] };
    const options = { method: 'POST', body: '{}' };
    const mocked = t.mock.method(globalThis, 'fetch', async () => Response.json(data));
    assert.deepEqual(await requestJson('/api/analyze', options), data);
    assert.deepEqual(mocked.mock.calls[0].arguments, ['/api/analyze', options]);
  });
});
