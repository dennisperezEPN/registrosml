# Ventas POS (Django + PostgreSQL + Docker)

Sistema básico para registrar ventas de un pequeño local (MVP).

## Alcance (MVP)
- Registrar venta
- Listado de ventas por día
- Listado de ventas por producto
- Una sola caja
- Cierre de caja diario
- CRUD productos
- Stock de productos

## Requisitos
- Docker Desktop (Windows/Mac) o Docker Engine (Linux)
- Docker Compose (incluido en Docker Desktop)
- Git (opcional, para clonar)

## Estructura del proyecto
- `docker-compose.yml` → servicios `web` (Django) y `db` (PostgreSQL)
- `.env.example` → plantilla de variables de entorno (SIN secretos)
- `.env` → variables reales (NO se sube al repositorio)
- `backend/` → código Django + Dockerfile + requirements

## Inicio rápido

### 1) Clonar el repositorio
```bash
git clone <URL_DEL_REPO>
cd <NOMBRE_DEL_REPO>
```

### 2) Crear un archivo `env`
Este proyecto usa variables de entorno para credenciales y configuración:
POSTGRES_DB=ventas_db
POSTGRES_USER=ventas_user
POSTGRES_PASSWORD=change_me

DJANGO_SECRET_KEY=change_me
DJANGO_DEBUG=1

### 3) Construir y levantar contenedores
```bash
docker compose build
docker compose up -d
```

### 4) Migraciones y superusuario
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 5) Acceder al sistema
App: http://localhost:8000/
Admin: http://localhost:8000/admin


