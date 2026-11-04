#!/usr/bin/env bash
# Run explicitly with sudo on a fresh Ubuntu VM. Uses Docker's signed apt repo.
set -euo pipefail
[[ $(id -u) -eq 0 ]] || { echo 'Execute: sudo bash scripts/install-docker-ubuntu.sh' >&2; exit 1; }
. /etc/os-release
[[ ${ID:-} == ubuntu ]] || { echo 'Este instalador é para Ubuntu.' >&2; exit 1; }
if command -v docker > /dev/null; then
  docker version
  docker compose version || { echo 'Instale o plugin Compose pelo mesmo canal do Docker existente.' >&2; exit 1; }
  echo 'Docker já instalado. A instalação existente foi preservada.'
  exit 0
fi
apt-get update
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
architecture=$(dpkg --print-architecture)
cat > /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${UBUNTU_CODENAME:-$VERSION_CODENAME}
Components: stable
Architectures: $architecture
Signed-By: /etc/apt/keyrings/docker.asc
EOF
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
docker version
docker compose version
echo 'Docker pronto. Para iniciar: sudo bash scripts/ubuntu-up.sh'
