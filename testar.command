#!/bin/sh
cd -- "$(dirname -- "$0")" || exit 1
sh scripts/docker.sh test
status=$?
printf '\nTestes encerrados (código %s). Pressione Enter para fechar.\n' "$status"
read -r reply
exit "$status"
