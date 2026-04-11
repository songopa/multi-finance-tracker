"""
Pytest configuration and shared fixtures for backend tests
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import timedelta

from database import Base, get_db
from main import app
from models import User, UserRole, Entity, TransactionCategory, TransactionType
from auth import hash_password, create_access_token
from config import settings


# Use in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///test_finance_tracker.db"


@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh test database for each test function.
    """
    # Create test database engine
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        """Override the get_db dependency"""
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Yield the database
    db = TestingSessionLocal()
    yield db
    db.close()
    
    # Clean up - drop all tables and remove the database file
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(TEST_DATABASE_URL.replace("sqlite:///", "")):
        os.remove(TEST_DATABASE_URL.replace("sqlite:///", ""))


@pytest.fixture(scope="function")
def client(test_db):
    """
    Create a test client for making requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user(test_db):
    """
    Create a test user in the database.
    """
    user = User(
        email="testuser@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("testpassword123"),
        role=UserRole.CLIENT,
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user_token(test_user):
    """
    Create a JWT token for the test user.
    """
    token = create_access_token(
        user_id=test_user.id,
        email=test_user.email,
        role=test_user.role,
        expires_delta=timedelta(hours=1),
    )
    return token


@pytest.fixture(scope="function")
def test_user_headers(test_user_token):
    """
    Create headers with the test user's token.
    """
    return {
        "Authorization": f"Bearer {test_user_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="function")
def test_entity(test_db, test_user):
    """
    Create a test entity for the test user.
    """
    entity = Entity(
        owner_id=test_user.id,
        name="Test Financial Entity",
        description="A test entity for transactions",
        entity_type="personal",
        is_active=True,
    )
    test_db.add(entity)
    test_db.commit()
    test_db.refresh(entity)
    return entity


@pytest.fixture(scope="function")
def test_category_income(test_db):
    """
    Create a test income category.
    """
    category = TransactionCategory(
        name="Salary",
        description="Regular salary",
        type=TransactionType.INCOME,
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture(scope="function")
def test_category_expense(test_db):
    """
    Create a test expense category.
    """
    category = TransactionCategory(
        name="Groceries",
        description="Grocery shopping",
        type=TransactionType.EXPENSE,
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture(scope="function")
def test_admin(test_db):
    """
    Create a test admin user in the database.
    """
    admin = User(
        email="testadmin@example.com",
        username="testadmin",
        full_name="Test Admin",
        hashed_password=hash_password("adminpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def test_admin_token(test_admin):
    """
    Create a JWT token for the test admin.
    """
    token = create_access_token(
        user_id=test_admin.id,
        email=test_admin.email,
        role=test_admin.role,
        expires_delta=timedelta(hours=1),
    )
    return token


@pytest.fixture(scope="function")
def test_admin_headers(test_admin_token):
    """
    Create headers with the test admin's token.
    """
    return {
        "Authorization": f"Bearer {test_admin_token}",
        "Content-Type": "application/json",
    }
