#!/bin/sh
set -eu
export PGCLIENTENCODING=UTF8
for script in roles_grants schema rls seeds; do
 psql -v ON_ERROR_STOP=1 --username postgres --dbname securedb -f "/lab-sql/$script.sql"
done
