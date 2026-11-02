#!/usr/bin/env bash
# ==============================================================================
# Script: setup-swarm-dind.sh
# Finalidade: Criar um cluster Docker Swarm (1 Manager + 2 Workers)
#            utilizando Docker-in-Docker (DinD) em um único host Ubuntu.
# Referência: Livro "Descomplicando o Docker"
# ==============================================================================

set -e

echo "=== 1. Limpando nós anteriores (se existirem) ==="
docker rm -f swarm-manager swarm-worker-1 swarm-worker-2 2>/dev/null || true
docker network rm swarm-dind-net 2>/dev/null || true

echo "=== 2. Criando rede bridge para comunicação entre os nós ==="
docker network create --driver bridge swarm-dind-net

echo "=== 3. Iniciando container Manager ==="
docker run -d --privileged \
  --name swarm-manager \
  --hostname swarm-manager \
  --network swarm-dind-net \
  -p 80:80 \
  -p 8080:8080 \
  -p 5000:5000 \
  docker:dind

# Aguarda o daemon do Docker inicializar dentro do container
echo "Aguardando Docker daemon no manager..."
sleep 4

echo "=== 4. Inicializando Docker Swarm no Manager ==="
docker exec swarm-manager docker swarm init

echo "=== 5. Obtendo Join-Token de Worker e IP do Manager ==="
TOKEN=$(docker exec swarm-manager docker swarm join-token worker -q)
MANAGER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' swarm-manager)

echo "Manager IP: $MANAGER_IP"
echo "Join Token: $TOKEN"

echo "=== 6. Iniciando Worker 1 e associando ao Swarm ==="
docker run -d --privileged \
  --name swarm-worker-1 \
  --hostname swarm-worker-1 \
  --network swarm-dind-net \
  docker:dind

sleep 3
docker exec swarm-worker-1 docker swarm join --token "$TOKEN" "${MANAGER_IP}:2377"

echo "=== 7. Iniciando Worker 2 e associando ao Swarm ==="
docker run -d --privileged \
  --name swarm-worker-2 \
  --hostname swarm-worker-2 \
  --network swarm-dind-net \
  docker:dind

sleep 3
docker exec swarm-worker-2 docker swarm join --token "$TOKEN" "${MANAGER_IP}:2377"

echo ""
echo "=============================================================================="
echo "Cluster Docker Swarm criado com sucesso!"
echo "Status dos nós:"
docker exec swarm-manager docker node ls
echo "=============================================================================="
echo "Para acessar o manager:"
echo "  docker exec -it swarm-manager sh"
echo ""
