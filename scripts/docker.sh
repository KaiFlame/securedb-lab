#!/bin/sh
# POSIX shell: all application dependencies run inside Linux containers.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
export LOCAL_UID="$(id -u)" LOCAL_GID="$(id -g)"
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-securedb-lab}
export COMPOSE_PROJECT_NAME

fail() { printf '\n%s\n' "$*" >&2; exit 1; }
dc() { docker compose -p "$COMPOSE_PROJECT_NAME" -f "$ROOT/docker-compose.yml" "$@"; }
bc() { docker compose -p "${COMPOSE_PROJECT_NAME}-bootstrap" -f "$ROOT/compose.bootstrap.yml" "$@"; }
port() { sed -n 's/^WEB_PORT=\([0-9][0-9]*\)$/\1/p' .env | tail -n 1; }

docker_ready() {
    if ! command -v docker >/dev/null 2>&1; then
        for candidate in "$HOME/.docker/bin" /Applications/Docker.app/Contents/Resources/bin; do
            if [ -x "$candidate/docker" ]; then PATH="$candidate:$PATH"; export PATH; break; fi
        done
    fi
    command -v docker >/dev/null 2>&1 || fail 'Instale o Docker Desktop: https://docs.docker.com/desktop/setup/install/mac-install/ . Depois abra o Docker e aceite a configuração inicial.'
    docker compose version >/dev/null 2>&1 || fail 'Docker Compose v2 ausente. Atualize o Docker Desktop.'
    if ! docker info >/dev/null 2>&1; then
        if [ "$(uname -s)" = Darwin ] && [ -d /Applications/Docker.app ]; then
            printf 'Abrindo Docker Desktop; aguardando o motor (até 120 segundos)...\n'
            open -a Docker
            count=0
            until docker info >/dev/null 2>&1; do
                count=$((count+1))
                [ "$count" -le 60 ] || fail 'Docker não ficou disponível. Conclua a configuração no Docker Desktop e tente novamente.'
                sleep 2
            done
        else
            fail 'O motor Docker está indisponível. Abra o Docker Desktop ou inicie o Docker Engine e tente novamente.'
        fi
    fi
    [ "$(docker info --format '{{.OSType}}')" = linux ] || fail 'Selecione contêineres Linux no Docker Desktop.'
}

setup() {
    printf 'Preparando configuração local, certificados e credenciais...\n'
    bc build bootstrap
    bc run --rm --no-deps -T bootstrap setup
}

diagnose() {
    [ -f .env ] || fail 'Configuração ausente. Execute primeiro: sh scripts/docker.sh up'
    mkdir -p .local/inspection
    rm -f evidencias/environment.json
    for service in postgres mongo; do
        cid=$(dc ps -q "$service")
        [ -n "$cid" ] || fail "Contêiner ausente: $service"
        # No Config.Env, passwords, full documents, or Docker socket in the bootstrap.
        docker inspect --format "{\"service\":\"$service\",\"running\":{{json .State.Running}},\"image\":{{json .Config.Image}},\"port_bindings\":{{json .HostConfig.PortBindings}},\"networks\":{{json .NetworkSettings.Networks}}}" "$cid" > ".local/inspection/$service.json"
    done
    docker network inspect --format '{"Name":{{json .Name}},"Internal":{{json .Internal}}}' "${COMPOSE_PROJECT_NAME}_data" > .local/inspection/network.json
    bc run --rm --no-deps -T bootstrap diagnose
}

ops() { dc --profile tools run --rm --no-deps -T ops "$@"; }
action=${1:-up}
[ "$#" -eq 0 ] || shift
case "$action" in
    up|test|down|diagnose|backup|restore|report|credentials) ;;
    *) fail 'Uso: sh scripts/docker.sh up|test|down|diagnose|backup|restore|report|credentials [--database sql|nosql|both]' ;;
esac
if [ "$action" = credentials ]; then
    [ -f .local/ACESSO_LOCAL.txt ] || fail 'Execute up antes de consultar os acessos.'
    cat .local/ACESSO_LOCAL.txt
    exit 0
fi
docker_ready
case "$action" in
    up)
        setup
        dc config --quiet
        dc up -d --build --wait --wait-timeout 300
        diagnose
        printf '\nAplicação: http://localhost:%s\nAcessos: .local/ACESSO_LOCAL.txt\n' "$(port)"
        if [ "$(uname -s)" = Darwin ] && [ "${LAB_NO_BROWSER:-0}" != 1 ]; then open "http://localhost:$(port)"; fi
        ;;
    down) dc down; printf 'Serviços parados. Dados e credenciais preservados.\n' ;;
    diagnose) diagnose ;;
    test)
        diagnose
        dc --profile tools build ops
        ops pytest tests -q -p no:cacheprovider
        ;;
    backup|restore)
        dc --profile tools build ops
        ops python scripts/backup_restore.py "$@"
        ;;
    report)
        dc --profile tools build ops
        ops python scripts/report.py
        ;;
esac
