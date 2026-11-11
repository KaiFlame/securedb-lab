#!/bin/sh
set -eu
mkdir -p /tmp/pg-tls
cp /lab-certs/server.crt /tmp/pg-tls/server.crt
cp /lab-certs/server.key /tmp/pg-tls/server.key
chown -R postgres:postgres /tmp/pg-tls
chmod 600 /tmp/pg-tls/server.key
exec /usr/local/bin/docker-entrypoint.sh postgres -c config_file=/etc/securedb/postgresql.conf
