"""
Integration and unit tests for entity routes
"""
import pytest
from fastapi import status

from models import Entity


class TestEntityCreation:
    """Tests for creating entities"""
    
    def test_create_entity_success(self, client, test_user_headers):
        """Test successfully creating an entity"""
        entity_data = {
            "name": "My Business",
            "description": "My business operations",
            "entity_type": "business",
        }
        
        response = client.post("/entities/", json=entity_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "My Business"
        assert data["description"] == "My business operations"
        assert data["entity_type"] == "business"
        assert data["is_active"] is True
        assert "id" in data
    
    def test_create_entity_minimal(self, client, test_user_headers):
        """Test creating entity with minimal data"""
        entity_data = {
            "name": "Simple Entity",
        }
        
        response = client.post("/entities/", json=entity_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Simple Entity"
        assert data["description"] is None
    
    def test_create_entity_duplicate_name(self, client, test_user_headers, test_entity):
        """Test creating entity with duplicate name for same user"""
        entity_data = {
            "name": test_entity.name,
            "description": "Different description",
        }
        
        response = client.post("/entities/", json=entity_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already have" in response.json()["detail"]
    
    def test_create_entity_unauthorized(self, client):
        """Test creating entity without authentication"""
        entity_data = {"name": "My Entity"}
        
        response = client.post("/entities/", json=entity_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEntityRetrieval:
    """Tests for retrieving entities"""
    
    def test_list_entities_success(self, client, test_user_headers, test_db, test_user):
        """Test successfully listing entities"""
        # Create multiple entities
        for i in range(3):
            entity = Entity(
                owner_id=test_user.id,
                name=f"Entity {i}",
                entity_type="personal",
            )
            test_db.add(entity)
        test_db.commit()
        
        response = client.get("/entities/", headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3
    
    def test_list_entities_empty(self, client, test_user_headers):
        """Test listing entities when none exist"""
        response = client.get("/entities/", headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0
    
    def test_list_entities_filter_active(self, client, test_user_headers, test_db, test_user):
        """Test filtering entities by active status"""
        # Create active and inactive entities
        active = Entity(owner_id=test_user.id, name="Active", is_active=True)
        inactive = Entity(owner_id=test_user.id, name="Inactive", is_active=False)
        test_db.add_all([active, inactive])
        test_db.commit()
        
        # Get only active
        response = client.get("/entities/?is_active=true", headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(e["is_active"] for e in data)
    
    def test_get_entity_success(self, client, test_user_headers, test_entity):
        """Test getting a specific entity"""
        response = client.get(f"/entities/{test_entity.id}", headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_entity.id
        assert data["name"] == test_entity.name
    
    def test_get_entity_not_found(self, client, test_user_headers):
        """Test getting non-existent entity"""
        response = client.get("/entities/9999", headers=test_user_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_entity_different_user(self, client, test_db, test_user):
        """Test getting entity owned by different user"""
        from auth import hash_password
        
        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=hash_password("password"),
            role="client",
        )
        test_db.add(other_user)
        test_db.commit()
        
        # Create entity owned by other user
        other_entity = Entity(
            owner_id=other_user.id,
            name="Other's Entity",
        )
        test_db.add(other_entity)
        test_db.commit()
        
        # Try to access with first user
        headers = {
            "Authorization": f"Bearer {create_access_token(test_user.id, test_user.email, test_user.role)}",
        }
        response = client.get(f"/entities/{other_entity.id}", headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestEntityUpdate:
    """Tests for updating entities"""
    
    def test_update_entity_success(self, client, test_user_headers, test_db, test_entity):
        """Test successfully updating an entity"""
        update_data = {
            "name": "Updated Entity Name",
            "description": "Updated description",
        }
        
        response = client.put(f"/entities/{test_entity.id}", json=update_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Entity Name"
        assert data["description"] == "Updated description"
    
    def test_update_entity_partial(self, client, test_user_headers, test_entity):
        """Test partial entity update"""
        update_data = {
            "description": "Just update description",
        }
        
        response = client.put(f"/entities/{test_entity.id}", json=update_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Just update description"
        assert data["name"] == test_entity.name  # Unchanged
    
    def test_update_entity_toggle_active(self, client, test_user_headers, test_entity):
        """Test toggling entity active status"""
        update_data = {
            "is_active": False,
        }
        
        response = client.put(f"/entities/{test_entity.id}", json=update_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is False
    
    def test_update_entity_not_found(self, client, test_user_headers):
        """Test updating non-existent entity"""
        update_data = {"name": "Updated"}
        
        response = client.put("/entities/9999", json=update_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_entity_duplicate_name(self, client, test_user_headers, test_db, test_user):
        """Test updating to name that already exists"""
        entity1 = Entity(owner_id=test_user.id, name="Entity 1")
        entity2 = Entity(owner_id=test_user.id, name="Entity 2")
        test_db.add_all([entity1, entity2])
        test_db.commit()
        
        # Try to rename entity2 to entity1's name
        update_data = {"name": "Entity 1"}
        response = client.put(f"/entities/{entity2.id}", json=update_data, headers=test_user_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestEntityDeletion:
    """Tests for deleting entities"""
    
    def test_delete_entity_success(self, client, test_user_headers, test_db, test_entity):
        """Test successfully deleting an entity"""
        entity_id = test_entity.id
        
        response = client.delete(f"/entities/{entity_id}", headers=test_user_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        deleted = test_db.query(Entity).filter(Entity.id == entity_id).first()
        assert deleted is None
    
    def test_delete_entity_not_found(self, client, test_user_headers):
        """Test deleting non-existent entity"""
        response = client.delete("/entities/9999", headers=test_user_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_entity_unauthorized(self, client, test_user_headers, test_db):
        """Test deleting entity owned by different user"""
        from auth import hash_password, create_access_token
        from models import User
        
        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password=hash_password("password"),
            role="client",
        )
        test_db.add(other_user)
        test_db.commit()
        
        # Create entity for other user
        other_entity = Entity(owner_id=other_user.id, name="Other's Entity")
        test_db.add(other_entity)
        test_db.commit()
        
        # Try to delete with current user
        response = client.delete(f"/entities/{other_entity.id}", headers=test_user_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


# Import necessary items for tests
from models import User
from auth import create_access_token
