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

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new client user
- `POST /auth/login` - Login and receive JWT tokens
- `POST /auth/refresh` - Refresh access token

### Users (`/users`)
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `POST /users/change-password` - Change password

### Admin (`/admin`)
- `POST /admin/register` - Register new admin (should be restricted)
- `GET /admin/dashboard/stats` - Get dashboard statistics
- `GET /admin/users` - List all users (with filtering)
- `GET /admin/users/{user_id}` - Get specific user
- `PUT /admin/users/{user_id}/deactivate` - Deactivate user
- `PUT /admin/users/{user_id}/activate` - Activate user
- `DELETE /admin/users/{user_id}` - Delete user
- `GET /admin/actions` - Audit log of admin actions

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── database.py          # Database setup
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # Authentication utilities
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
└── routes/              # API route handlers
    ├── __init__.py
    ├── auth.py          # Authentication routes
    ├── users.py         # User profile routes
    └── admin.py         # Admin management routes
```

## Database Models

### User
Represents both clients and admins with roles and verification status.

### Entity
Financial contexts owned by clients (personal, freelance, business, etc.)

### Transaction
Income and expense records within entities with categories

### TransactionCategories
Categorization for income and expenses

### AdminAction
Audit log for all admin actions on the system

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Access Token**: Short-lived token for API requests (default: 30 minutes)
2. **Refresh Token**: Long-lived token for getting new access tokens (default: 7 days)

All protected endpoints require an `Authorization: Bearer <token>` header.



