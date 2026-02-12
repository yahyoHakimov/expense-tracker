# Expense Tracker API

REST API for expense management with JWT authentication.

## Features

- User authentication (JWT)
- CRUD operations for expenses
- Filter by date (week, month, 3 months, custom)
- Filter by category
- Expense summary & statistics
- Modern responsive UI

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- JWT Authentication (Argon2)
- Docker

## Quick Start

### 1. Clone & Setup
```bash
git clone <repo-url>
cd expense-tracker

# Create .env file
cp .env.example .env

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
# Add to .env
```

### 2. Run with Docker
```bash
docker-compose up --build
```

Open: http://localhost:8000

### 3. Manual Setup (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL
docker run --name expense-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=expense_db \
  -p 5434:5432 -d postgres

# Run application
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register
- `POST /auth/login` - Login (get JWT token)
- `GET /auth/me` - Current user info

### Expenses
- `POST /expenses/` - Create expense
- `GET /expenses/` - List expenses (with filters)
- `GET /expenses/{id}` - Get single expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense
- `GET /expenses/summary/stats` - Expense summary

### Query Parameters
```
?period=week|month|3months
?start_date=2026-01-01&end_date=2026-01-31
?category=groceries|leisure|electronics|utilities|clothing|health|others
```

## Project Structure
```
expense-tracker/
├── app/
│   ├── main.py           # FastAPI app
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── auth.py           # JWT + password hashing
│   ├── dependencies.py   # get_current_user
│   ├── database.py       # DB connection
│   └── routers/
│       ├── auth.py       # Auth endpoints
│       └── expenses.py   # Expense endpoints
├── frontend/
│   └── index.html        # UI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## Categories

- Groceries
- Leisure
- Electronics
- Utilities
- Clothing
- Health
- Others

## API Documentation

Swagger UI: http://localhost:8000/docs

## License

MIT