# Multi-Finance Tracker Frontend

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Run the Application

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

> Make sure the backend is running on `http://localhost:8000` before starting the frontend.

## Pages

### Authentication
- `/login` - Sign in with email and password
- `/register` - Create a new account (auto logs in after registration)

### App
- `/` - Dashboard — income vs expenses summary with category breakdown
- `/entities` - Create and manage financial entities (personal, freelance, business)
- `/categories` - Create and manage income/expense categories
- `/transactions` - Record and view income/expense transactions
- `/reports` - Generate financial reports with date range filtering

## Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx              # App entry point
    ├── App.jsx               # Routes and auth guards
    ├── index.css             # Global styles
    ├── api/
    │   ├── client.js         # Axios instance with JWT interceptor
    │   ├── entities.js       # Entity API calls
    │   ├── categories.js     # Category API calls
    │   ├── transactions.js   # Transaction API calls
    │   └── reports.js        # Report API calls
    ├── components/
    │   └── Navbar.jsx        # Navigation bar
    └── pages/
        ├── Login.jsx
        ├── Register.jsx
        ├── Dashboard.jsx
        ├── Entities.jsx
        ├── Categories.jsx
        ├── Transactions.jsx
        └── Reports.jsx
```

## Authentication

JWT tokens are stored in `localStorage` under the key `token`. The axios client automatically attaches the token to every request. On a 401 response the token is cleared and the user is redirected to `/login`.

Protected routes redirect unauthenticated users to `/login`. Login and register pages redirect authenticated users to `/`.