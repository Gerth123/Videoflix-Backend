# 🧠 Videoflix Backend (Django + DRF)

Dies ist das Backend für die Videoflix-Plattform. Es stellt REST-APIs zur Verfügung für Userverwaltung, Authentifizierung, Video-Daten, Thumbnails und mehr.

## 🔧 Technologien

- Django 4+
- Django Rest Framework
- Django RQ (Background Tasks)
- PostgreSQL
- Django Debug Toolbar
- **FFmpeg** (für Videobearbeitung / Thumbnails)

## ⚙️ Installation & Entwicklung

Funktioniert unter **Linux** und **Windows**.

### 🔹 Windows (PowerShell)

```powershell
# Umgebung anlegen und aktivieren
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt

# Migration und Serverstart
python manage.py migrate
python manage.py runserver
```

### 🔸 Linux

```bash
# Umgebung anlegen und aktivieren
python -m venv env_lin
source env_lin/bin/activate
pip install -r requirementslin.txt

# Migration und Serverstart
python manage.py migrate
python manage.py runserver
```

> Backend läuft lokal unter `http://127.0.0.1:8000`

### 🎥 FFmpeg installieren

Für die Erstellung von Thumbnails aus Videos muss FFmpeg installiert sein:

#### Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```
## ⚡ Redis-Server starten (nur Linux)

1. Virtuelle Umgebung aktivieren:

```bash
source env_lin/bin/activate
```

2. Redis-Server starten:

```bash
redis-server
```

3. In einem **neuen Terminal**, erneut die Umgebung aktivieren und den Worker starten:

```bash
source env_lin/bin/activate
python manage.py rqworker default
```

4. In einem weiteren Terminal dann den Server:

```bash
python manage.py runserver
```

## 🔑 API-Endpunkte (gekürzt)

### 🔐 Auth & Benutzer

| Pfad                          | Beschreibung                        |
|-------------------------------|-------------------------------------|
| `/api/registration/`          | Registrierung                      |
| `/api/login/`                 | Login                               |
| `/api/activate/<uid>/<tok>/`  | Konto aktivieren                    |
| `/api/auth/password-reset/`   | Passwort-Reset anfordern           |
| `/api/auth/password-reset-confirm/` | Passwort-Reset bestätigen   |
| `/api/profiles/`              | Benutzerprofil-Liste               |
| `/api/profiles/<id>/`         | Profil-Details                     |

### 🎮 Videos & Genres

| Pfad                              | Beschreibung                        |
|-----------------------------------|-------------------------------------|
| `/api/videos/`                    | Liste aller Videos                 |
| `/api/videos/<id>/`               | Video-Detailansicht                |
| `/api/videos/<id>/thumbnail/`     | Einzelnes Thumbnail                |
| `/api/genres/`                    | Gruppierung nach Genres           |
| `/api/big-thumbnail/`            | Großes Thumbnail für Startseite    |

## 📂 Media

Statische Mediendateien (z. B. Video-Thumbnails) werden über:

```
/media/<pfad-zum-bild>
```

ausgeliefert. Stelle sicher, dass `MEDIA_URL` und `MEDIA_ROOT` korrekt gesetzt sind.

## 🛡️ Sensible Variablen (E-Mail, DB-Zugang)

Sensible Daten wie E-Mail-Zugangsdaten oder das Datenbankpasswort sind **ausgelagert in eine separate Datei**:

```python
from static.variables import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DB_PASSWORD, SECRET_KEY


## 🧪 Debug & Background

- `__debug__/` – Debug Toolbar
- `django-rq/` – Task Queue Dashboard

## 📌 Hinweis

Dieses Backend ist optimiert für die Zusammenarbeit mit dem Angular-Frontend. Für CORS oder Authentifizierung per Token kann zusätzlich `django-cors-headers` oder `SimpleJWT` genutzt werden.

