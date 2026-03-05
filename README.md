# TaskFlow — Task & Project Manager

A full-featured task and project management web application built with Django, deployed using Docker, Nginx, and PostgreSQL on a cloud server with a complete CI/CD pipeline.

> **DSCC Coursework 1** | Westminster International University in Tashkent

---

## Features

- **User Authentication** — Register, login, logout with session management
- **Project Management** — Create, edit, delete projects with status tracking
- **Task CRUD** — Full create/read/update/delete operations for tasks
- **Priority & Status** — Tasks have Low/Medium/High priority and To Do/In Progress/Done status
- **Categories (Tags)** — Many-to-many tagging system with color-coded labels
- **Progress Tracking** — Visual progress bars per project
- **Dashboard** — Overview of all projects and recent tasks
- **User Profile** — Personal stats page
- **Admin Panel** — Django admin configured for all models
- **Responsive UI** — Bootstrap 5, works on mobile and desktop

---

## Technologies Used

| Layer | Technology |
|-------|------------|
| Backend | Django 4.2, Python 3.11 |
| Database | PostgreSQL 15 |
| Web Server | Nginx 1.25 |
| App Server | Gunicorn |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Frontend | Bootstrap 5, Bootstrap Icons |

---

## Database Schema

```
User (Django built-in)
  │
  └── Project (many-to-one: many projects per user)
        │
        └── Task (many-to-one: many tasks per project)
              │
              └── Category (many-to-many: tasks can have multiple categories)
```

---

## Local Setup (Development)

### Prerequisites
- Docker Desktop installed
- Git installed

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/00016532/taskflow.git
cd taskflow

# 2. Copy environment file
cp .env.example .env

# 3. Start with Docker Compose (development mode)
docker compose -f docker-compose.local.yml up --build

# 4. Run migrations
docker compose -f docker-compose.local.yml exec web python manage.py migrate

# 5. Create superuser
docker compose -f docker-compose.local.yml exec web python manage.py createsuperuser

# 6. Visit the app
# App:   http://localhost:8000
# Admin: http://localhost:8000/admin
```

---

## Deployment Instructions (Production)

### 1. Set up the server

```bash
# SSH into your server
ssh ubuntu@4.223.87.102

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Clone and configure on server

```bash
sudo mkdir -p /opt/taskflow
cd /opt/taskflow
git clone https://github.com/00016532/taskflow.git .

# Create production .env
cp .env.example .env
nano .env
```

### 3. Start services

```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py createsuperuser
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-random-secret` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed domains | `itstask.duckdns.org` |
| `POSTGRES_DB` | Database name | `taskmanager` |
| `POSTGRES_USER` | DB username | `postgres` |
| `POSTGRES_PASSWORD` | DB password | `strongpassword` |
| `POSTGRES_HOST` | DB hostname | `db` |
| `DOMAIN` | Your domain | `itstask.duckdns.org` |
| `ADMIN_EMAIL` | Admin email | `you@email.com` |

---

## GitHub Actions Secrets Required

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `SSH_PRIVATE_KEY` | Private key to SSH into server |
| `SSH_HOST` | Server IP address |
| `SSH_USERNAME` | SSH username |

---

## Live Demo

- **Application:** http://itstask.duckdns.org
- **Docker Hub:** https://hub.docker.com/r/drbekzod/taskflow

### Test Credentials
- Username: `admin`
- Password: `1234`
