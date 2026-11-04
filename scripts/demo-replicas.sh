#!/usr/bin/env bash
# Declarative 1 -> 2 -> 1 scale demo; never fabricates cluster evidence.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# -eq 0 || ($# -eq 1 && $1 == --auto) ]] || { echo 'Uso: bash scripts/demo-replicas.sh [--auto]' >&2; exit 2; }
: "${BACKEND_IMAGE:?Defina BACKEND_IMAGE}"
: "${FRONTEND_IMAGE:?Defina FRONTEND_IMAGE}"
: "${MONITOR_IMAGE:?Defina MONITOR_IMAGE}"
output_dir=${DEMO_OUTPUT_DIR:-artifacts/swarm-demo/$(date +%Y%m%d-%H%M%S)}
mkdir -p "$output_dir"
for stage in 1 2 3; do
  replicas=1
  if [[ $stage == 2 ]]; then replicas=2; fi
  echo "=== Etapa $stage: $replicas réplica(s) de frontend e backend ==="
  APP_REPLICAS=$replicas WITH_VISUALIZER=1 bash scripts/deploy-swarm.sh
  docker node ls > "$output_dir/step-$stage-nodes.txt"
  docker stack services autobudget > "$output_dir/step-$stage-services.txt"
  docker stack ps --no-trunc autobudget > "$output_dir/step-$stage-tasks.txt"
  printf 'Etapa %s: APP_REPLICAS=%s\n' "$stage" "$replicas" > "$output_dir/step-$stage.txt"
  echo "Abra http://IP_DO_MANAGER:${VISUALIZER_PORT:-8081} e capture o gráfico desta etapa."
  if [[ ${1:-} != --auto ]]; then
    read -r -p 'Após capturar o Visualizer, pressione Enter para continuar. ' _ || {
      echo 'Sem entrada interativa. Use --auto para executar sem pausas.' >&2; exit 1;
    }
  fi
done
echo "Demonstração concluída. Evidências reais em $output_dir. O cluster terminou com 1 réplica por serviço."
echo 'Para voltar a 2: APP_REPLICAS=2 bash scripts/deploy-swarm.sh'
