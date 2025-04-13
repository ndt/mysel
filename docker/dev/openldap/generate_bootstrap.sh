#!/bin/bash

generate_ssha() {
    local password="$1"
    local salt=$(openssl rand -base64 6)
    local hash_salt=$(echo -n "$password$salt" | openssl dgst -sha1 -binary | (
        cat
        echo -n "$salt"
    ) | base64)
    echo "{SSHA}$hash_salt"
}

PASSWORD="meinpasswort"
HASH=$(generate_ssha "$PASSWORD")

echo "openLDAP User initialisieren"
# Lade Umgebungsvariablen
cd "$(dirname "${BASH_SOURCE[0]}")"
source ../.env.dev

# Erstelle Bootstrap-Verzeichnisse
mkdir -p bootstrap/ldif

# Generiere User LDIF
cat > bootstrap/ldif/02-users.ldif << EOF
# Create people OU
dn: ou=people,dc=$(echo $LDAP_DOMAIN | cut -d. -f1),dc=$(echo $LDAP_DOMAIN | cut -d. -f2)
objectClass: top
objectClass: organizationalUnit
ou: people

EOF

# Generiere User Einträge
for i in {1..3}; do
    PASSWORD="${LDAP_USER_PASSWORD}${i}"
    HASH=$(generate_ssha "$PASSWORD")
    
    cat >> bootstrap/ldif/02-users.ldif << EOF
# User $i
dn: uid=testuser${i},ou=people,dc=$(echo $LDAP_DOMAIN | cut -d. -f1),dc=$(echo $LDAP_DOMAIN | cut -d. -f2)
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
objectClass: upnUser
cn: Test User${i}
sn: User${i}
uid: testuser${i}
mail: testuser${i}@${MAIL_DOMAIN}
userPrincipalName: testuser${i}@${LDAP_DOMAIN}
userPassword: ${HASH}
mailLoginByLdap: TRUE

EOF
done

echo "openLDAP-User wurden erstellt"
