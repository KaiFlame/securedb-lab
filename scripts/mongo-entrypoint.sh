#!/bin/bash
set -euo pipefail
mkdir -p /tmp/mongo-tls
cp /lab-certs/server.pem /tmp/mongo-tls/server.pem
cp /lab-certs/ca.crt /tmp/mongo-tls/ca.crt
chown -R mongodb:mongodb /tmp/mongo-tls /data/db
chmod 600 /tmp/mongo-tls/server.pem
if [ ! -f /data/db/.securedb-initialized ]; then
  # Temporary initialization listens only on loopback and is never reachable by peers.
  gosu mongodb mongod --dbpath /data/db --bind_ip 127.0.0.1 --port 27018 --fork --logpath /tmp/mongo-init.log
  trap 'gosu mongodb mongod --dbpath /data/db --shutdown || true' EXIT
  mongosh --quiet --port 27018 /lab-nosql/users_roles.js
  gosu mongodb mongod --dbpath /data/db --shutdown
  touch /data/db/.securedb-initialized
  chown mongodb:mongodb /data/db/.securedb-initialized
  trap - EXIT
fi
exec gosu mongodb mongod --config /etc/securedb/mongod.conf
