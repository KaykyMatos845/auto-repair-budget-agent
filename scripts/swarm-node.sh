#!/usr/bin/env bash
# Run locally on each VM with permission to access Docker.
set -euo pipefail
role=${1:-}
private_ip=${2:-}
manager_ip=${3:-}
if [[ "$role" != manager && "$role" != worker ]] || [[ -z "$private_ip" ]]; then
  echo 'Usage: bash scripts/swarm-node.sh manager PRIVATE_IP' >&2
  echo '       bash scripts/swarm-node.sh worker PRIVATE_IP MANAGER_IP < worker-token.txt' >&2
  exit 2
fi
state=$(docker info --format '{{.Swarm.LocalNodeState}}')
if [[ "$state" != inactive ]]; then
  echo "Swarm state is $state; leaving existing cluster unchanged. Inspect docker info before continuing." >&2
  exit 1
fi
if [[ "$role" == manager ]]; then
  # Capture Docker output: init otherwise prints a reusable join credential.
  if output=$(docker swarm init --advertise-addr "$private_ip" 2>&1); then
    echo 'Manager initialized. Run docker node ls to verify.'
    echo 'Save worker token securely: (umask 077; docker swarm join-token -q worker > worker-token.txt)'
  else
    echo "$output" >&2
    exit 1
  fi
else
  [[ -n "$manager_ip" ]] || { echo 'Manager private IP required' >&2; exit 2; }
  IFS= read -r token
  [[ -n "$token" ]] || { echo 'Worker token required on stdin' >&2; exit 2; }
  docker swarm join --advertise-addr "$private_ip" --token "$token" "${manager_ip}:2377"
  unset token
fi
