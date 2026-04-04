# Multi-Finance Tracker Backend

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Important settings:
- `DATABASE_URL`: Database connection string (uses SQLite by default)
- `SECRET_KEY`: JWT secret key (change to a strong random string in production)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default: 30)

### 3. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Default Admin User

On first startup, a default admin user is created:
- Email: `admin@mft.com`
- Username: `admin`
- Password: `admin123`

**IMPORTANT**: Change the default password immediately in production!

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Access Token**: Short-lived token for API requests (default: 30 minutes)
2. **Refresh Token**: Long-lived token for getting new access tokens (default: 7 days)

All protected endpoints require an `Authorization: Bearer <token>` header.



