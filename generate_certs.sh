#!/bin/bash
set -e

# Konfigurationsvariablen
BASE_DIR="$(pwd)"
CA_DIR="certificates"
SERVICES=("mailserver" "openldap")
VALIDITY_DAYS=3650
COUNTRY="DE"
STATE="Berlin"
LOCALITY="Berlin"
ORGANIZATION="ExampleOrg"
CA_CN="Root CA"

# Hilfsfunktion für Fehlerbehandlung
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Verzeichnisse prüfen und erstellen
check_and_create_directories() {
    echo "Checking directory structure..."
    
    for service in "${SERVICES[@]}"; do
        if [ ! -d "${service}" ]; then
            error_exit "Service directory '${service}' not found! Please create service directories first."
        fi
    done

    mkdir -p "${CA_DIR}/root-ca"
    for service in "${SERVICES[@]}"; do
        mkdir -p "${CA_DIR}/${service}"
    done
}

# Root CA erstellen
create_root_ca() {
    echo "Creating Root CA..."
    if [ ! -f "${CA_DIR}/root-ca/root-ca.key" ]; then
        openssl genrsa -out "${CA_DIR}/root-ca/root-ca.key" 4096 || error_exit "Failed to create CA key"
        openssl req -x509 -new -nodes \
            -key "${CA_DIR}/root-ca/root-ca.key" \
            -sha256 \
            -days 3650 \
            -out "${CA_DIR}/root-ca/root-ca.crt" \
            -subj "/C=${COUNTRY}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION}/CN=${CA_CN}" \
            || error_exit "Failed to create CA certificate"
    else
        echo "Root CA already exists, skipping..."
    fi
}

# Service-Zertifikate erstellen
create_service_cert() {
    local service=$1
    echo "Creating certificate for ${service}..."
    
    openssl genrsa -out "${CA_DIR}/${service}/${service}.key" 2048 \
        || error_exit "Failed to create key for ${service}"

    openssl req -new \
        -key "${CA_DIR}/${service}/${service}.key" \
        -out "${CA_DIR}/${service}/${service}.csr" \
        -subj "/C=${COUNTRY}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION}/CN=${service}.test" \
        || error_exit "Failed to create CSR for ${service}"

    openssl x509 -req \
        -in "${CA_DIR}/${service}/${service}.csr" \
        -CA "${CA_DIR}/root-ca/root-ca.crt" \
        -CAkey "${CA_DIR}/root-ca/root-ca.key" \
        -CAcreateserial \
        -out "${CA_DIR}/${service}/${service}.crt" \
        -days ${VALIDITY_DAYS} \
        || error_exit "Failed to sign certificate for ${service}"

    rm "${CA_DIR}/${service}/${service}.csr"

    # Kopiere Zertifikate in Service-Verzeichnis
    cp "${CA_DIR}/root-ca/root-ca.crt" "${service}/"
    cp "${CA_DIR}/${service}/${service}.key" "${service}/"
    cp "${CA_DIR}/${service}/${service}.crt" "${service}/"
}

# Hauptfunktion
main() {
    echo "Starting certificate generation process..."
    
    check_and_create_directories
    create_root_ca
    
    for service in "${SERVICES[@]}"; do
        create_service_cert "${service}"
    done
    
    echo "Certificate generation completed successfully!"
    echo "Certificates have been copied to each service directory."
    echo ""
    echo "Make sure your Dockerfiles include:"
    echo "COPY root-ca.crt /usr/local/share/ca-certificates/"
    echo "COPY \${service}.key /etc/ssl/private/"
    echo "COPY \${service}.crt /etc/ssl/certs/"
    echo "RUN update-ca-certificates"
}

main
