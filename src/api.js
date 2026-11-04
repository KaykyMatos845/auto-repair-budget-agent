const CONNECTION_HELP = 'Confira se o servidor Python está aberto na porta 5000 e consulte o erro no terminal dele.';

export async function requestJson(url, options) {
  let response;
  let body;
  try {
    response = await fetch(url, options);
    body = await response.text();
  } catch {
    throw new Error(`Não foi possível receber a resposta do servidor. ${CONNECTION_HELP}`);
  }

  const status = `HTTP ${response.status}`;
  if (!body.trim()) {
    throw new Error(`O servidor retornou uma resposta vazia (${status}). ${CONNECTION_HELP}`);
  }
  let data;
  try {
    data = JSON.parse(body);
  } catch {
    throw new Error(`O servidor retornou uma resposta inválida (${status}). ${CONNECTION_HELP}`);
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    throw new Error(`O servidor retornou uma resposta inválida (${status}). ${CONNECTION_HELP}`);
  }
  if (!response.ok || data.error) {
    throw new Error((data.error || 'O servidor não concluiu a solicitação.') + ` (Código: ${data.code || status})`);
  }
  return data;
}
