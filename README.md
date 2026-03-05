# 📋 TaskFlow — Task & Project Manager

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
| SSL | Let's Encrypt (Certbot) |
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
git clone https://github.com/YOUR_USERNAME/taskflow.git
cd taskflow

# 2. Copy environment file
cp .env.example .env
# Edit .env and set DEBUG=True for development

# 3. Start with Docker Compose (development mode)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# 4. Create superuser (in a new terminal)
docker compose exec web python manage.py createsuperuser

# 5. Visit the app
# App:   http://localhost:8000
# Admin: http://localhost:8000/admin
```

---

## Deployment Instructions (Production)

### 1. Set up the server

```bash
# SSH into your server
ssh user@YOUR_SERVER_IP

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Configure firewall
sudo ufw allow 22   # SSH
sudo ufw allow 80   # HTTP
sudo ufw allow 443  # HTTPS
sudo ufw enable
```

### 2. Clone and configure on server

```bash
sudo mkdir -p /opt/taskflow
cd /opt/taskflow
git clone https://github.com/YOUR_USERNAME/taskflow.git .

# Create production .env
cp .env.example .env
nano .env  # Fill in real values
```

### 3. Get SSL certificate

```bash
# Get certificate using certbot
docker compose --profile certbot run certbot

# Update nginx/nginx.conf with your real domain name
```

### 4. Start services

```bash
docker compose up -d
docker compose exec web python manage.py createsuperuser
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-random-secret` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed domains | `yourdomain.uz` |
| `POSTGRES_DB` | Database name | `taskmanager` |
| `POSTGRES_USER` | DB username | `taskmanager_user` |
| `POSTGRES_PASSWORD` | DB password | `strongpassword` |
| `POSTGRES_HOST` | DB hostname | `db` |
| `DOMAIN` | Your domain | `yourdomain.uz` |
| `ADMIN_EMAIL` | For SSL cert | `you@email.com` |

---

## GitHub Actions Secrets Required

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `SSH_PRIVATE_KEY` | Private key to SSH into server |
| `SSH_HOST` | Server IP address |
| `SSH_USERNAME` | SSH username (usually `ubuntu`) |

---

## Screenshots

*(Add screenshots of your running application here)*

---

## Live Demo

- **Application:** https://yourdomain.uz
- **Docker Hub:** https://hub.docker.com/r/YOUR_USERNAME/taskflow

### Test Credentials
- Username: `demo`
- Password: `demo1234`
