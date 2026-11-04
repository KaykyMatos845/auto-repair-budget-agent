#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${BACKEND_IMAGE:?Set shared registry backend image with immutable version tag}"
: "${FRONTEND_IMAGE:?Set shared registry frontend image with immutable version tag}"
[[ $(docker info --format '{{.Swarm.ControlAvailable}}') == true ]] || { echo 'Run on the manager VM' >&2; exit 1; }
ready=$(docker node ls --filter status=ready --format '{{.Availability}}' | awk '$0=="Active" {n++} END {print n+0}')
[[ "$ready" -ge 2 ]] || { echo 'Need two Ready/Active nodes' >&2; exit 1; }
docker stack config -c docker-compose.yml > /dev/null
docker stack deploy --with-registry-auth -c docker-compose.yml autobudget
docker stack services autobudget
echo 'Deployment submitted; inspect docker stack ps autobudget and validate the UI/API before declaring readiness.'
