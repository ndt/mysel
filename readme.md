# Email Authentication PoC

## Übersicht
Dieser Proof of Concept (PoC) demonstriert eine sichere Authentifizierungslösung für E-Mail-Dienste, die sowohl OAuth2 für Webmail als auch gerätebasierte Authentifizierungen für native E-Mail-Clients unterstützt.

## Hauptfunktionen
- Webmail-Zugriff via OAuth2/OIDC
- Verwaltung von Geräte-spezifischen Passwörtern über Webinterface
- Automatische Deaktivierung der LDAP-Authentifizierung nach Einrichtung von Geräte-Passwörtern
- Selfservice-Portal für Benutzer

## Komponenten
- OpenLDAP (Benutzerverwaltung)
- Keycloak (Identity Provider)
- PostgreSQL (Datenbank)
- Roundcube (Webmail-Client)
- Dovecot/Postfix (Mailserver)
- Django (Selfservice-Portal)
## Voraussetzungen
- Docker und Docker Compose
- OpenSSL
- Bearbeitung der `/etc/hosts` Datei

## Installation

### 1. Hosts-Einträge
Fügen Sie folgende Einträge in `/etc/hosts` hinzu:
```
127.0.0.1 myselfservice
127.0.0.1 keycloak
127.0.0.1 roundcube
```

### 2. Initialisierung
```bash
./init.sh
```
Dieses Script generiert die notwendigen Konfigurationen basierend auf der `.env` Datei.

### 3. Start des Systems
```bash
docker compose up --build
```

## Neustart nach Konfigurationsänderungen
Bei Änderungen an der Konfiguration:
```bash
docker compose down --volumes
docker compose up --build
```

## Hinweis
Alle Docker Volumes müssen entfernt werden, wenn Konfigurationsänderungen vorgenommen wurden, da sich einige Services sonst nicht korrekt neu initialisieren.
