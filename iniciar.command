#!/bin/sh
cd -- "$(dirname -- "$0")" || exit 1
sh scripts/docker.sh up
status=$?
if [ "$status" -ne 0 ]; then
    printf '\nFalha ao iniciar. Leia a mensagem acima. Pressione Enter para fechar.\n'
    read -r reply
fi
exit "$status"
