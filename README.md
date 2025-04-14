
---

## 🧠 Backend – `videoflix-backend/README.md`

```markdown
# 🧠 Videoflix Backend (Django + DRF)

Dies ist das Backend für die Videoflix-Plattform. Es stellt REST-APIs zur Verfügung für Userverwaltung, Authentifizierung, Video-Daten, Thumbnails und mehr.

## 🔧 Technologien

- Django 4+
- Django Rest Framework
- Django RQ (Background Tasks)
- SQLite / PostgreSQL
- Django Debug Toolbar

## ⚙️ Installation & Entwicklung

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
