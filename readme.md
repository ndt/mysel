# Email Authentication PoC

## Übersicht
Dieser Proof of Concept (PoC) demonstriert eine Authentifizierungslösung für E-Mail-Dienste, die sowohl OAuth2 für Webmail als auch gerätebasierte Authentifizierungen für native E-Mail-Clients (Thunderbird, etc.) unterstützt.

## Hauptfunktionen
- Webmail-Zugriff via OAuth2/OIDC
- Selfservice-Portal für Benutzer
 - Verwaltung von Geräte-spezifischen Passwörtern über Webinterface
- Automatische Deaktivierung der LDAP-Authentifizierung nach Einrichtung von Geräte-Passwörtern

## Komponenten
- OpenLDAP (Benutzerverwaltung)
- Keycloak (Identity Provider)
- PostgreSQL (Datenbank)
- Roundcube (Webmail-Client)
- Dovecot/Postfix (Mailserver)
- Django (Selfservice-Portal)

## Voraussetzungen
- Docker und Docker Compose
- OpenSSL (um die LDAP-Passwörter zu generieren)
- Bearbeitung der `/etc/hosts` Datei
- Browser auf dem Docker-Host-System

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

Das `init.sh` Script automatisiert die initiale Einrichtung:

- Erstellt eine `.env` Datei aus der `env.example`
- Ersetzt Platzhalter in verschiedenen Konfigurationsdateien mit den tatsächlichen Werten aus der `.env`
- Konfiguriert Git so, dass sensible Dateien nicht versehentlich committed werden aber trotzdem Teil des repositories sind
- ruft ein weiteres Script `openldap/generate_bootstrap.sh` auf um OpenLDAP zu vorzubereiten

Mit dem `--reverse` Parameter können die Ersetzungen an den Konfigurationsdateien rückgängig gemacht werden. Das ist notwendig, wenn Änderungen an den Konfigurationsdateien vorgenommen werden soll und eingecheckt werden sollen.

### 3. Start des Systems und Nutzung
```bash
docker compose up --build
```
- Anmeldung an Webmail http://roundcube:8081 (SSO) und LDAP-Zugangsdaten (Username: testuser1@example.org, Passwort: testuser1)
- Anmelden an imap (localhost:143 STARTTLS) mit LDAP-Zugangsdaten (siehe z.B. `simple-tests.sh`)
- Anmelden an Django-Webinterface (SSO (Username: testuser1@example.org, Passwort: testuser1)) -> Email-Konten -> Account generieren
- Anschließend wieder testen mit `simple-tests.sh`


## Neustart nach Konfigurationsänderungen
Bei Änderungen an der Konfiguration:
```bash
docker compose down --volumes
docker compose up --build
```

## Hinweis
Alle Docker Volumes müssen entfernt werden (`docker compose down --volumes`), wenn Konfigurationsänderungen vorgenommen wurden, da sich einige Services sonst nicht korrekt neu initialisieren.
