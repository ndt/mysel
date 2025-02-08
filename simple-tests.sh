#!/bin/bash
source .env

# Array mit Test-Credentials
declare -A TESTUSERS=(
    ["testuser1@example.org"]="${LDAP_USER_PASSWORD}1"
    ["testuser1_96@example.org"]="tVsk-iBnS-zbrT"
    ["testuser2@example.org"]="${LDAP_USER_PASSWORD}2"
    ["testuser2_85@example.org"]="Vi1a-8We9-6Pg9"
)


SERVER="localhost"
PORT="143"

test_imap_login() {
    local username="$1"
    local password="$2"
    local commands="/tmp/imap_commands.$$"

    # IMAP-Kommandos erstellen
    cat > "${commands}" << EOF
a001 LOGIN $username $password
a005 LOGOUT
EOF
    # Verbindung testen
    (cat "${commands}") | \
    openssl s_client -connect $SERVER:$PORT -starttls imap -quiet 2>/dev/null| \
    while IFS= read -r line; do
        echo "$line" | tr -d '\r'
        [[ "$line" == *"a001 NO"* ]] && echo "Login fehlgeschlagen!" && exit 1
    done &
    local pid=$!

    # Timeout-Handler
    sleep 30 && kill $pid 2>/dev/null &
    local kill_pid=$!

    wait $pid
    kill $kill_pid 2>/dev/null
    rm "${commands}"
}

# LDAP Tests
echo "Testing LDAP..."
echo -n "  Admin connection... "
if ldapsearch -x -H ldap://localhost -b dc=example,dc=org -D "cn=admin,dc=example,dc=org" -w $LDAP_ADMIN_PASSWORD uid=testuser1 > /dev/null 2>&1; then
    echo -e "OK"
else
    echo -e "FAILED"
fi

echo -n "   User connection... "
if ldapsearch -x -H ldap://localhost -b uid=testuser1,ou=people,dc=example,dc=org -D "uid=testuser1,ou=people,dc=example,dc=org" -w "${LDAP_USER_PASSWORD}1" > /dev/null 2>&1; then
    echo -e "OK"
else
    echo -e "FAILED"
fi
echo "=== Starting Mail Server Tests ==="


# Teste alle Benutzer
for username in "${!TESTUSERS[@]}"; do
    echo "Testing $username..."
    test_imap_login "$username" "${TESTUSERS[$username]}"
done
