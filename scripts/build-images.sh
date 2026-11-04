#!/usr/bin/env bash
# No publication unless --push is explicitly supplied.
set -euo pipefail
cd "$(dirname "$0")/.."
backend_image=${BACKEND_IMAGE:-autobudget-backend:local}
frontend_image=${FRONTEND_IMAGE:-autobudget-frontend:local}
[[ $# -eq 0 || ($# -eq 1 && $1 == --push) ]] || { echo 'Uso: bash scripts/build-images.sh [--push]' >&2; exit 2; }
push_images=false
if [[ ${1:-} == --push ]]; then
  : "${BACKEND_IMAGE:?Defina uma imagem em registro HTTPS compartilhado}"
  : "${FRONTEND_IMAGE:?Defina uma imagem em registro HTTPS compartilhado}"
  for image in "$backend_image" "$frontend_image"; do
    registry=${image%%/*}
    [[ $image == */* && $registry != localhost* && $registry != 127.* && $image != *:latest && ${image##*/} == *:* ]] || {
      echo 'Use imagens de um registro compartilhado com tag de versão; não use localhost nem latest.' >&2; exit 2;
    }
  done
  push_images=true
fi
build_options=()
if [[ -n ${PROXY_CA_FILE:-} ]]; then
  [[ -r $PROXY_CA_FILE ]] || { echo 'PROXY_CA_FILE não é legível' >&2; exit 2; }
  build_options+=(--secret "id=proxy_ca,src=$PROXY_CA_FILE")
fi
docker build "${build_options[@]}" -f Dockerfile.backend -t "$backend_image" .
docker build "${build_options[@]}" -f Dockerfile.frontend -t "$frontend_image" .
if $push_images; then
  docker push "$backend_image"
  docker push "$frontend_image"
fi
echo 'Imagens prontas; modelo incluído e verificado no backend.'
