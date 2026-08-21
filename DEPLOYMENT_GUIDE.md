# EC Carbon Survey - Django Backend Deployment Guide

## Quick Start

### 1. Prerequisites

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib postgis

# macOS with Homebrew
brew install postgresql postgis
```

### 2. Database Setup

```bash
sudo -u postgres psql

CREATE DATABASE ec_survey_db;
CREATE USER survey_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ec_survey_db TO survey_user;

\c ec_survey_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

\q
```

### 3. Environment Setup

```bash
cd django_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
cat > ec_survey/.env << EOF
DJANGO_SECRET_KEY=your-secret-key-here-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
DB_NAME=ec_survey_db
DB_USER=survey_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
EOF
```

### 4. Migrate and Create Superuser

```bash
cd ec_survey
python manage.py migrate
python manage.py createsuperuser
# Enter username, email, password

# Load mock data (optional)
python manage.py import_mock

# Run development server
python manage.py runserver 0.0.0.0:8000
```

### 5. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login/` | POST | Login, get token |
| `/api/auth/register/` | POST | Register new user |
| `/api/auth/me/` | GET | Current user info |
| `/api/plots/` | GET/POST | List/create plots |
| `/api/plots/<id>/` | GET/PATCH/DELETE | Plot detail |
| `/api/plots/submit_survey/` | POST | Submit survey from mobile |
| `/api/trees/` | GET/POST | Tree measurements |
| `/api/soil/` | GET/POST | Soil samples |
| `/api/water/` | GET/POST | Water assessments |
| `/api/socioeconomic/` | GET/POST | Socio-economic data |
| `/api/stats/summary/` | GET | All statistics |
| `/api/stats/forest_types/` | GET | Forest type breakdown |
| `/api/stats/provinces/` | GET | Province breakdown |
| `/api/stats/species/` | GET | Species counts |
| `/api/stats/dbh_distribution/` | GET | DBH histogram data |
| `/api/stats/soil/` | GET | Soil analysis |
| `/api/stats/timeline/` | GET | Collection timeline |
| `/api/stats/waypoints/` | GET | GPS waypoint counts |
| `/api/stats/water/` | GET | Water source breakdown |
| `/api/stats/socioeconomic/` | GET | Socio-economic summary |

### 6. Production Deployment

```bash
# Install Gunicorn
pip install gunicorn whitenoise

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn ec_survey.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Or use systemd
```

### 7. Configure Frontend API URL

In the frontend `src/lib/env.ts`, set your backend URL:

```typescript
const DEV_API = 'https://your-django-server.com';
```

Or use environment variable:
```bash
VITE_API_URL=https://your-django-server.com npm run build
```

## Authentication

The API uses Token Authentication:

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Response: {"token":"abc123...","user":{"id":1,"username":"admin"}}

# Use token in subsequent requests
curl http://localhost:8000/api/plots/ \
  -H "Authorization: Token abc123..."
```

## CORS

The backend allows all origins in development. For production, configure:

```python
# settings.py
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
    "https://your-android-app.com",
]
```
