#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

printf 'This removes all Random Pass and local Elastic data volumes. Continue? [y/N] '
read -r confirmation
case "$confirmation" in
  y|Y|yes|YES)
    ;;
  *)
    printf 'Reset cancelled.\n'
    exit 0
    ;;
esac

cd "$ROOT_DIR"
docker compose --profile demo down -v --remove-orphans
docker compose -f elastic-start-local/docker-compose.yml down -v --remove-orphans

printf 'Random Pass demo data has been removed. Run ./bootstrap.sh for a clean start.\n'