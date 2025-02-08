#!/bin/bash

source .env

echo "exclude files from git repo"
git update-index --assume-unchanged keycloak/import/realm-export.json
git update-index --assume-unchanged mailserver/dovecot-sql.conf.ext
git update-index --assume-unchanged mailserver/dovecot-ldap.conf.ext
git update-index --assume-unchanged postgres/init-django-db.sh
git update-index --assume-unchanged postgres/init-roundcube-db.sh
git update-index --assume-unchanged roundcube/config/config.local.inc.php

echo "change passwords and secrets in various files"

# Keycloak
sed -i "s/DJANGO_OIDC_SECRET/${DJANGO_OIDC_SECRET}/g" keycloak/import/realm-export.json
sed -i "s/LDAP_ADMIN_PASSWORD/${LDAP_ADMIN_PASSWORD}/g" keycloak/import/realm-export.json
sed -i "s/ROUNDCUBEMAIL_OIDC_SECRET/${ROUNDCUBEMAIL_OIDC_SECRET}/g" keycloak/import/realm-export.json

# dovecot
sed -i "s/POSTGRES_DJANGO_DB/${POSTGRES_DJANGO_DB}/g" mailserver/dovecot-sql.conf.ext
sed -i "s/POSTGRES_DOVECOT_USER/${POSTGRES_DOVECOT_USER}/g" mailserver/dovecot-sql.conf.ext
sed -i "s/POSTGRES_DOVECOT_PASSWORD/${POSTGRES_DOVECOT_PASSWORD}/g" mailserver/dovecot-sql.conf.ext
sed -i "s/LDAP_ADMIN_PASSWORD/${LDAP_ADMIN_PASSWORD}/g" mailserver/dovecot-ldap.conf.ext

#postgres
sed -i "s/POSTGRES_DJANGO_DB/${POSTGRES_DJANGO_DB}/g" postgres/init-django-db.sh
sed -i "s/POSTGRES_DJANGO_USER/${POSTGRES_DJANGO_USER}/g" postgres/init-django-db.sh
sed -i "s/POSTGRES_DJANGO_PASSWORD/${POSTGRES_DJANGO_PASSWORD}/g" postgres/init-django-db.sh
sed -i "s/POSTGRES_DOVECOT_USER/${POSTGRES_DOVECOT_USER}/g" postgres/init-django-db.sh
sed -i "s/POSTGRES_DOVECOT_PASSWORD/${POSTGRES_DOVECOT_PASSWORD}/g" postgres/init-django-db.sh
sed -i "s/ROUNDCUBEMAIL_DB_USER/${ROUNDCUBEMAIL_DB_USER}/g" postgres/init-roundcube-db.sh
sed -i "s/ROUNDCUBEMAIL_DB_NAME/${ROUNDCUBEMAIL_DB_NAME}/g" postgres/init-roundcube-db.sh
sed -i "s/ROUNDCUBEMAIL_DB_PASSWORD/${ROUNDCUBEMAIL_DB_PASSWORD}/g" postgres/init-roundcube-db.sh

#roundcube
sed -i "s/ROUNDCUBEMAIL_OIDC_SECRET/${ROUNDCUBEMAIL_OIDC_SECRET}/g" roundcube/config/config.local.inc.php

# openLDAP
set -e
./openldap/generate_bootstrap.sh


