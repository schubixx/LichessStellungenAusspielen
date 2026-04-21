# Lichess AI Starter (Flask + SQLite + Blueprints)

Dieses Projekt ist eine Flask-Webanwendung für Python, die:

- den Benutzer per OAuth bei Lichess anmeldet,
- das Access-Token serverseitig in SQLite speichert,
- danach eine Seite mit 3 FEN-Buttons anzeigt,
- und beim Klick auf einen Button eine Partie gegen die Lichess-KI startet und in einem neuen Browser-Fenster öffnet.

## Projektstruktur

```text
lichess_flask_project/
├── app/
│   ├── auth/
│   │   └── routes.py
│   ├── game/
│   │   └── routes.py
│   ├── main/
│   │   └── routes.py
│   ├── static/css/
│   │   └── style.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── error.html
│   │   ├── fen_select.html
│   │   └── index.html
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   └── utils.py
├── instance/
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

## Voraussetzungen

- Python 3.10+
- Ein Lichess API/OAuth-Client

## Lichess konfigurieren

Lege in Lichess eine Anwendung an und trage als Redirect URI dieselbe URI ein wie in deiner `.env`.

Beispiel:

```env
LICHESS_REDIRECT_URI=http://127.0.0.1:5000/auth/callback
```

## Installation

### 1. Projekt in Visual Studio öffnen

Du kannst den Projektordner direkt in **Visual Studio** oder **Visual Studio Code** öffnen.

### 2. Virtuelle Umgebung anlegen

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. Umgebungsdatei anlegen

Kopiere `.env.example` nach `.env` und trage deine Werte ein:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=bitte-aendern
LICHESS_CLIENT_ID=deine-client-id
LICHESS_REDIRECT_URI=http://127.0.0.1:5000/auth/callback
DATABASE_URL=sqlite:///lichess_tokens.db
```

## Starten

```bash
python run.py
```

Danach im Browser öffnen:

```text
http://127.0.0.1:5000/
```

## Verhalten

1. Startseite öffnen
2. Auf **Mit Lichess verbinden** klicken
3. OAuth-Freigabe bei Lichess erteilen
4. Danach auf der FEN-Auswahlseite landen
5. Auf einen der drei Buttons klicken
6. Die Partie wird erzeugt und in einem neuen Browser-Tab/Fenster geöffnet

## SQLite

Die SQLite-Datenbank wird automatisch erstellt, sobald die App startet.

Tabelle:

- `lichess_tokens`

Gespeicherte Daten:

- `lichess_user_id`
- `lichess_username`
- `access_token`
- `scope`
- Timestamps

## Wichtige Hinweise

- Die Tokens werden **serverseitig** gespeichert, nicht im Browser.
- Die Beispiel-FENs kannst du in `app/config.py` anpassen.
- Die AI-Parameter wie Level, Uhr und Farbe kannst du ebenfalls in `app/config.py` ändern.
- Falls Lichess ein Token widerrufen hat, muss sich der Nutzer erneut anmelden.

## Empfehlenswerte nächste Erweiterungen

- Verschlüsselung der Tokens in der Datenbank
- Benutzerverwaltung in der eigenen App
- Mehr als 3 Presets, z. B. aus SQLite oder einer Admin-Oberfläche
- Konfigurierbare AI-Stufe und Farbe im Frontend
- Logging und Fehler-Monitoring
