#!/usr/bin/env bash
set -euo pipefail

deployment_directory="${1:-/opt/json-workbench}"
cd -- "$deployment_directory"

docker compose config --quiet
docker compose pull
docker compose up -d --no-deps --force-recreate --wait --wait-timeout 120 prometheus
docker compose up -d --wait --wait-timeout 120
docker compose ps
