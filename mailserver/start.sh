#!/bin/bash
#set -e

wait_for() {
    echo "Waiting for $1"
    while ! nc -z $2 $3; do
        sleep 1
    done
    echo "$1 is up!"
}

#wait_for "PostgreSQL" ${POSTGRES_HOST:-postgres} 5432
#wait_for "LDAP" ${LDAP_HOST:-openldap} 389

# Konfiguration anpassen mit ENV Variablen

# Verzeichnisse und Berechtigungen
mkdir -p /var/spool/postfix/private
chown -R postfix:postfix /var/spool/postfix/
chmod -R 0700 /var/spool/postfix/private/

service dovecot start

/usr/sbin/postfix start-fg

