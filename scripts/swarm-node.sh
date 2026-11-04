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
[[ $role != worker || -n $manager_ip ]] || { echo 'Manager private IP required' >&2; exit 2; }
state=$(docker info --format '{{.Swarm.LocalNodeState}}')
if [[ $state == active ]]; then
  control=$(docker info --format '{{.Swarm.ControlAvailable}}')
  address=$(docker info --format '{{.Swarm.NodeAddr}}')
  if [[ $address == "$private_ip" && (($role == manager && $control == true) || ($role == worker && $control == false)) ]]; then
    if [[ $role == worker ]]; then
      docker info --format '{{range .Swarm.RemoteManagers}}{{println .Addr}}{{end}}' | \
        awk -v expected="${manager_ip}:2377" '$0 == expected {found=1} END {exit !found}' || {
          echo 'Este worker pertence a outro manager. Confira o cluster existente.' >&2; exit 1;
        }
    fi
    echo 'Este nó já está configurado no Swarm.'
    exit 0
  fi
fi
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
  IFS= read -r token || true
  [[ -n "$token" ]] || { echo 'Worker token required on stdin' >&2; exit 2; }
  docker swarm join --advertise-addr "$private_ip" --token "$token" "${manager_ip}:2377"
  unset token
fi
