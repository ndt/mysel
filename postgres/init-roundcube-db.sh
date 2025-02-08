#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER roundcube WITH PASSWORD 'roundcube';
	CREATE DATABASE roundcube;
	GRANT ALL PRIVILEGES ON DATABASE roundcube TO roundcube;
	ALTER DATABASE roundcube OWNER TO roundcube;
	GRANT ALL ON SCHEMA public TO roundcube;
EOSQL

