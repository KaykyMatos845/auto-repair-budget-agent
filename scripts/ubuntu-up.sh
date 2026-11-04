#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker info > /dev/null
docker compose version > /dev/null
compose_files=(-f compose.ubuntu.yml)
if [[ -n ${PROXY_CA_FILE:-} ]]; then
  compose_files+=(-f compose.ca.yml)
fi
docker compose "${compose_files[@]}" build
docker compose "${compose_files[@]}" up -d --no-build --wait --wait-timeout 180
docker compose "${compose_files[@]}" ps
binding=$(docker compose "${compose_files[@]}" port frontend 8080 | head -n 1)
echo "Auto Repair disponível. Abra http://IP_DO_UBUNTU:${binding##*:}"
