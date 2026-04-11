"""
Integration and unit tests for authentication routes
"""
import pytest
from fastapi import status
from datetime import timedelta

from models import User, UserRole


class TestUserRegistration:
    """Tests for user registration endpoint"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["role"] == "client"
        assert data["is_active"] is True
        assert "hashed_password" not in data
    
    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "securepassword123",
            "confirm_password": "differentpassword123",
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "do not match" in response.json()["detail"]
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        user_data = {
            "email": test_user.email,
            "username": "newusername",
            "full_name": "Another User",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username"""
        user_data = {
            "email": "different@example.com",
            "username": test_user.username,
            "full_name": "Another User",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        user_data = {
            "email": "not-an-email",
            "username": "newuser",
            "full_name": "New User",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Tests for user login endpoint"""
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123",
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword",
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword",
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, client, test_db):
        """Test login with inactive user"""
        from auth import hash_password
        
        # Create inactive user
        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=hash_password("testpassword123"),
            role=UserRole.CLIENT,
            is_active=False,
        )
        test_db.add(inactive_user)
        test_db.commit()
        
        login_data = {
            "email": inactive_user.email,
            "password": "testpassword123",
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "inactive" in response.json()["detail"]


class TestTokenRefresh:
    """Tests for token refresh endpoint"""
    
    def test_refresh_token_success(self, client, test_user_token):
        """Test successful token refresh"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        response = client.post("/auth/refresh", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["access_token"] != test_user_token  # New token should be different
    
    def test_refresh_token_missing_auth(self, client):
        """Test token refresh without authentication"""
        response = client.post("/auth/refresh")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_refresh_token_invalid_token(self, client):
        """Test token refresh with invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        
        response = client.post("/auth/refresh", headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
