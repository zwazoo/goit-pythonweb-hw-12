# Contacts API

REST API for storing and managing personal contacts, built with FastAPI, async SQLAlchemy, and PostgreSQL. Includes JWT authentication, email verification, rate limiting, CORS, and Cloudinary avatar uploads.

## Tech stack

- **FastAPI** — web framework
- **SQLAlchemy 2.x** (async) — ORM
- **asyncpg** — async PostgreSQL driver
- **Pydantic v2** + **pydantic-settings** — validation and config
- **PostgreSQL** — database
- **Alembic** — database migrations
- **PyJWT** — JWT tokens
- **pwdlib** (Argon2) — password hashing
- **fastapi-mail** + Mailtrap — email verification
- **Cloudinary** — avatar uploads
- **slowapi** — rate limiting
- **Docker Compose** — service orchestration

## Project structure

```
├── main.py                        # App entry point, CORS, rate limit handler
├── alembic/                       # Alembic migrations
├── docker-compose.yml
├── Dockerfile
└── src/
    ├── config.py                  # Settings via pydantic-settings (.env)
    ├── database/
    │   ├── connection.py          # Async engine, session, get_db
    │   └── models.py              # User and Contact ORM models
    ├── repository/
    │   ├── contacts.py            # Contact CRUD (scoped to current user)
    │   └── users.py               # User DB queries
    ├── services/
    │   ├── auth.py                # JWT tokens, password hashing, get_current_user
    │   ├── users.py               # Gravatar, Cloudinary upload
    │   ├── email.py               # Email sending via fastapi-mail
    │   └── contacts.py            # Birthday logic
    ├── routers/
    │   ├── auth.py                # /auth — signup, login, refresh, email verification
    │   ├── users.py               # /users — profile, avatar upload
    │   └── contacts.py            # /contacts — CRUD, birthday search
    └── schemas/
        ├── users.py               # User request/response schemas
        └── contacts.py            # Contact request/response schemas
```

## Setup

### 1. Clone and create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:

```env
DB_NAME=contacts_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_DOMAIN=postgres        # use "localhost" when running without Docker
DB_PORT=5432

HASH_ALGORITHM=HS256
HASH_SECRET=your_secret_key_here

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

MAIL_USERNAME=your_mailtrap_username
MAIL_PASSWORD=your_mailtrap_password
MAIL_FROM=noreply@contacts.app

PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin
```

### 3. Run with Docker Compose

```bash
docker-compose up --build -d
```

### 4. Apply migrations

```bash
docker-compose exec app alembic upgrade head
```

Services:
- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- pgAdmin: `http://localhost:5050`

## API endpoints

### Auth

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/signup` | Register a new user |
| `POST` | `/auth/login` | Login, returns access + refresh tokens |
| `POST` | `/auth/refresh` | Refresh access token |
| `GET` | `/auth/confirmed_email/{token}` | Confirm email address |
| `POST` | `/auth/request_email` | Resend confirmation email |

### Users *(requires auth)*

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/users/me` | Current user profile *(max 3 req/min)* |
| `PATCH` | `/users/avatar` | Upload avatar to Cloudinary |

### Contacts *(requires auth, scoped to current user)*

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/contacts/` | List contacts (supports search) |
| `POST` | `/contacts/` | Create a new contact |
| `GET` | `/contacts/{id}` | Get contact by ID |
| `PUT` | `/contacts/{id}` | Update contact |
| `DELETE` | `/contacts/{id}` | Delete contact |
| `GET` | `/contacts/birthdays` | Contacts with birthdays in the next 7 days |

### Other

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Database health check |

## Migrations

```bash
# Generate migration from model changes
docker-compose exec app alembic revision --autogenerate -m "description"

# Apply
docker-compose exec app alembic upgrade head

# Rollback one step
docker-compose exec app alembic downgrade -1
```

## Error responses

| Status | Reason |
|--------|--------|
| `401` | Invalid credentials or unconfirmed email |
| `404` | Resource not found |
| `409` | Email already exists |
| `422` | Validation error |
| `429` | Rate limit exceeded |
