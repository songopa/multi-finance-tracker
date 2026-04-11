"""
Integration and unit tests for admin routes
"""
import pytest
from fastapi import status

from models import User, UserRole, AdminAction


class TestAdminDashboard:
    """Tests for admin dashboard statistics"""
    
    def test_get_dashboard_stats_success(self, client, test_admin_headers):
        """Test successfully retrieving dashboard statistics"""
        response = client.get("/admin/dashboard/stats", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_users" in data
        assert "total_clients" in data
        assert "total_admins" in data
        assert "active_users" in data
        assert "inactive_users" in data
        assert "new_users_today" in data
        assert "recent_admin_actions" in data
        assert isinstance(data["recent_admin_actions"], list)
    
    def test_get_dashboard_stats_unauthorized(self, client, test_user_headers):
        """Test that non-admin users cannot access dashboard"""
        response = client.get("/admin/dashboard/stats", headers=test_user_headers)
        
        # Should fail because test_user is not admin
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]
    
    def test_get_dashboard_stats_no_auth(self, client):
        """Test accessing dashboard without authentication"""
        response = client.get("/admin/dashboard/stats")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListAdminUsers:
    """Tests for listing users as admin"""
    
    def test_list_users_success(self, client, test_admin_headers, test_db):
        """Test successfully listing all users"""
        response = client.get("/admin/users", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_users_with_pagination(self, client, test_admin_headers):
        """Test listing users with pagination"""
        response = client.get("/admin/users?skip=0&limit=5", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 5
    
    def test_list_users_filter_by_role(self, client, test_admin_headers, test_db):
        """Test filtering users by role"""
        # Create a client user
        from auth import hash_password
        client_user = User(
            email="client@example.com",
            username="clientuser",
            hashed_password=hash_password("password"),
            role=UserRole.CLIENT,
        )
        test_db.add(client_user)
        test_db.commit()
        
        response = client.get("/admin/users?role=client", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(user["role"] == "client" for user in data)
    
    def test_list_users_filter_by_active(self, client, test_admin_headers, test_db):
        """Test filtering users by active status"""
        # Create an inactive user
        from auth import hash_password
        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=hash_password("password"),
            role=UserRole.CLIENT,
            is_active=False,
        )
        test_db.add(inactive_user)
        test_db.commit()
        
        response = client.get("/admin/users?is_active=true", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(user["is_active"] for user in data)
    
    def test_list_users_invalid_role(self, client, test_admin_headers):
        """Test listing users with invalid role filter"""
        response = client.get("/admin/users?role=invalid_role", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_list_users_unauthorized(self, client, test_user_headers):
        """Test that non-admin cannot list users"""
        response = client.get("/admin/users", headers=test_user_headers)
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]


class TestGetAdminUser:
    """Tests for retrieving specific user as admin"""
    
    def test_get_user_success(self, client, test_admin_headers, test_user):
        """Test successfully retrieving a user"""
        response = client.get(f"/admin/users/{test_user.id}", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
    
    def test_get_user_not_found(self, client, test_admin_headers):
        """Test retrieving non-existent user"""
        response = client.get("/admin/users/9999", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_user_unauthorized(self, client, test_user_headers, test_user):
        """Test that non-admin cannot get user details"""
        response = client.get(f"/admin/users/{test_user.id}", headers=test_user_headers)
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]


class TestDeactivateUser:
    """Tests for deactivating users"""
    
    def test_deactivate_user_success(self, client, test_admin_headers, test_db, test_user):
        """Test successfully deactivating a user"""
        response = client.put(f"/admin/users/{test_user.id}/deactivate", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert "deactivated" in response.json()["message"]
        
        # Verify user is deactivated
        updated_user = test_db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.is_active is False
    
    def test_deactivate_own_account(self, client, test_admin, test_admin_headers, test_db):
        """Test that admin cannot deactivate their own account"""
        response = client.put(f"/admin/users/{test_admin.id}/deactivate", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "own account" in response.json()["detail"]
    
    def test_deactivate_user_not_found(self, client, test_admin_headers):
        """Test deactivating non-existent user"""
        response = client.put("/admin/users/9999/deactivate", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_deactivate_user_unauthorized(self, client, test_user_headers, test_user):
        """Test that non-admin cannot deactivate users"""
        response = client.put(f"/admin/users/{test_user.id}/deactivate", headers=test_user_headers)
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]


class TestActivateUser:
    """Tests for activating users"""
    
    def test_activate_user_success(self, client, test_admin_headers, test_db):
        """Test successfully activating a deactivated user"""
        from auth import hash_password
        
        # Create inactive user
        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=hash_password("password"),
            role=UserRole.CLIENT,
            is_active=False,
        )
        test_db.add(inactive_user)
        test_db.commit()
        
        response = client.put(f"/admin/users/{inactive_user.id}/activate", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert "activated" in response.json()["message"]
        
        # Verify user is activated
        updated_user = test_db.query(User).filter(User.id == inactive_user.id).first()
        assert updated_user.is_active is True
    
    def test_activate_user_not_found(self, client, test_admin_headers):
        """Test activating non-existent user"""
        response = client.put("/admin/users/9999/activate", headers=test_admin_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_activate_user_unauthorized(self, client, test_user_headers, test_user):
        """Test that non-admin cannot activate users"""
        response = client.put(f"/admin/users/{test_user.id}/activate", headers=test_user_headers)
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]
