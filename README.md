# Multi-Finance Tracker

Most individuals manage finances from multiple contexts such as personal spending, freelance projects or small business but most budgeting tools allow only single context/entity. This project shall allow a person to track income and expenses from multiple entities/contexts. And within each entity they can record both income and expenses, categorize their transactions and generate reports of their finances.

## 🎯 Features
- User registration and authentication
- User can create multiple entities
- Record income transactions
- Record expense transactions
- Add transaction categories
- Generate reports per entity
- Simple charts 
- REST API endpoints for users, entities, transactions and categories


## 🛠️ Tech Stack

- **Backend** : FastAPI
- **Database**: SQLite
- **Frontend**: React

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip or pip3
- SQLite3

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multi-finance-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv mftenv
   # Windows
   mftenv\Scripts\activate
   # macOS/Linux
   source mftenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file
   echo "SECRET_KEY=<generate-secure-random-key>" > .env
   echo "DATABASE_URL=sqlite:///./finance_tracker.db" >> .env
   echo "ENVIRONMENT=development" >> .env
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```
   
   Server runs at: `http://localhost:8000`
   API docs: `http://localhost:8000/docs`

### Running Tests
```bash
pytest -v
pytest --cov=. --cov-report=html  # With coverage
```


## 👨‍💻 Development Team

- Julius Songopa
- Ferrin Mutuku

Multi-Finance Tracker - CSE 499 Senior Project
Brigham Young University, 2026
