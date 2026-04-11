"""
Integration and unit tests for user profile routes
"""
import pytest
from fastapi import status

from models import User


class TestUserProfile:
    """Tests for user profile endpoints"""
    
    def test_get_current_user_profile_success(self, client, test_user_headers, test_user):
        """Test successfully retrieving current user profile"""
        response = client.get("/users/me", headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["full_name"] == test_user.full_name
    
    def test_get_current_user_profile_unauthorized(self, client):
        """Test retrieving profile without authentication"""
        response = client.get("/users/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateUserProfile:
    """Tests for updating user profile"""
    
    def test_update_user_profile_success(self, client, test_user_headers, test_db, test_user):
        """Test successfully updating user profile"""
        update_data = {
            "full_name": "Updated User Name",
        }
        
        response = client.put("/users/me", json=update_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated User Name"
        
        # Verify database was updated
        updated_user = test_db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.full_name == "Updated User Name"
    
    def test_update_user_profile_clear_name(self, client, test_user_headers, test_db, test_user):
        """Test updating profile by clearing full name"""
        update_data = {
            "full_name": "",
        }
        
        response = client.put("/users/me", json=update_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should keep old name if empty string provided
        assert data["full_name"] == test_user.full_name
    
    def test_update_user_profile_unauthorized(self, client):
        """Test updating profile without authentication"""
        update_data = {"full_name": "New Name"}
        
        response = client.put("/users/me", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestChangePassword:
    """Tests for password change endpoint"""
    
    def test_change_password_success(self, client, test_user_headers, test_db, test_user):
        """Test successfully changing password"""
        password_data = {
            "old_password": "testpassword123",
            "new_password": "newpassword456",
        }
        
        response = client.post("/users/change-password", json=password_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert "successfully" in response.json()["message"]
        
        # Verify old password no longer works
        login_data = {
            "email": test_user.email,
            "password": "testpassword123",
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Verify new password works
        login_data_new = {
            "email": test_user.email,
            "password": "newpassword456",
        }
        login_response_new = client.post("/auth/login", json=login_data_new)
        assert login_response_new.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_old_password(self, client, test_user_headers):
        """Test changing password with incorrect old password"""
        password_data = {
            "old_password": "wrongoldpassword",
            "new_password": "newpassword456",
        }
        
        response = client.post("/users/change-password", json=password_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "incorrect" in response.json()["detail"]
    
    def test_change_password_unauthorized(self, client):
        """Test changing password without authentication"""
        password_data = {
            "old_password": "oldpassword",
            "new_password": "newpassword",
        }
        
        response = client.post("/users/change-password", json=password_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_change_password_too_short(self, client, test_user_headers):
        """Test changing password to one that's too short"""
        password_data = {
            "old_password": "testpassword123",
            "new_password": "short",
        }
        
        response = client.post("/users/change-password", json=password_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
