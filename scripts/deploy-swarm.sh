#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${BACKEND_IMAGE:?Set shared registry backend image with immutable version tag}"
: "${FRONTEND_IMAGE:?Set shared registry frontend image with immutable version tag}"
replicas=${APP_REPLICAS:-2}
[[ $replicas =~ ^[12]$ ]] || { echo 'APP_REPLICAS deve ser 1 ou 2 para duas VMs com uma réplica por nó.' >&2; exit 2; }
compose_files=(-c docker-compose.yml)
with_visualizer=${WITH_VISUALIZER:-1}
[[ $with_visualizer == 0 || $with_visualizer == 1 ]] || { echo 'WITH_VISUALIZER deve ser 0 ou 1.' >&2; exit 2; }
if [[ $with_visualizer == 1 ]]; then
  : "${MONITOR_IMAGE:?Defina a imagem do proxy de monitoramento no registro compartilhado}"
  compose_files+=(-c docker-compose.demo.yml)
fi
for image in "$BACKEND_IMAGE" "$FRONTEND_IMAGE" ${MONITOR_IMAGE:+"$MONITOR_IMAGE"}; do
  registry=${image%%/*}
  [[ $image == */* && $registry != localhost* && $registry != 127.* && $image != *:latest && ${image##*/} == *:* ]] || {
    echo 'Use imagens do registro compartilhado com tag de versão; localhost e latest não são aceitos.' >&2; exit 2;
  }
done
[[ $(docker info --format '{{.Swarm.ControlAvailable}}') == true ]] || { echo 'Run on the manager VM' >&2; exit 1; }
ready=$(docker node ls --filter status=ready --format '{{.Availability}}' | awk '$0=="Active" {n++} END {print n+0}')
[[ "$ready" -ge 2 ]] || { echo 'Need two Ready/Active nodes' >&2; exit 1; }
command -v curl > /dev/null || { echo 'Instale curl para validar a API antes de concluir.' >&2; exit 1; }
docker stack config "${compose_files[@]}" > /dev/null
docker stack deploy --with-registry-auth "${compose_files[@]}" autobudget
echo "Aguardando $replicas réplica(s) de cada serviço..."
deadline=$((SECONDS + 180))
ready_since=-1
while (( SECONDS < deadline )); do
  services=$(docker stack services autobudget --format '{{.Name}} {{.Replicas}}')
  updates=$(docker service inspect autobudget_backend autobudget_frontend --format '{{if .UpdateStatus}}{{.UpdateStatus.State}}{{else}}initial{{end}}')
  if grep -Eq '^(paused|rollback_started|rollback_paused|rollback_completed)$' <<< "$updates"; then
    docker stack services autobudget
    docker stack ps --no-trunc autobudget
    echo 'A implantação foi pausada ou sofreu rollback. A versão nova não foi confirmada.' >&2
    exit 1
  fi
  monitor_ready=true
  if [[ $with_visualizer == 1 ]]; then
    [[ $(awk '$1 ~ /^autobudget_(visualizer|monitor-proxy)$/ && $2=="1/1" {n++} END {print n+0}' <<< "$services") -eq 2 ]] || monitor_ready=false
    curl --fail --silent --max-time 5 "http://127.0.0.1:${VISUALIZER_PORT:-8081}/apis/nodes" | grep -Eq '"objects"[[:space:]]*:[[:space:]]*\[' || monitor_ready=false
  fi
  if [[ $(awk -v expected="$replicas/$replicas" '$1 ~ /^autobudget_(backend|frontend)$/ && $2==expected {n++} END {print n+0}' <<< "$services") -eq 2 ]] && $monitor_ready && \
    ! grep -q '^updating$' <<< "$updates" && \
    curl --fail --silent --max-time 5 "http://127.0.0.1:${APP_PORT:-8080}/api/health" | grep -q '"modelLoaded": true'; then
    if (( ready_since < 0 )); then ready_since=$SECONDS; fi
    if (( SECONDS - ready_since >= 15 )); then
      docker stack services autobudget
      echo "$replicas réplica(s) por serviço e API respondendo com o modelo carregado. Abra http://IP_DO_UBUNTU:${APP_PORT:-8080} e valide uma análise real."
      exit 0
    fi
  else
    ready_since=-1
  fi
  sleep 3
done
docker stack services autobudget
docker stack ps --no-trunc autobudget
echo 'A implantação não convergiu em 180 s. Confira os erros acima e docker service logs autobudget_backend.' >&2
exit 1
