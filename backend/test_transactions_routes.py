"""
Integration and unit tests for transactions routes (newer version)
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

from models import Transaction, TransactionType


class TestCreateTransaction:
    """Tests for creating transactions"""
    
    def test_create_transaction_success(self, client, test_user_headers, test_entity, test_category_income):
        """Test successfully creating a transaction"""
        transaction_data = {
            "entity_id": test_entity.id,
            "category_id": test_category_income.id,
            "transaction_type": "income",
            "amount": 5000,
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": datetime.now().isoformat(),
        }
        
        response = client.post(
            "/transactions/",
            json=transaction_data,
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["amount"] == 5000
        assert data["category"] == "Salary"
        assert data["transaction_type"] == "income"
    
    def test_create_transaction_type_mismatch(self, client, test_user_headers, test_entity, test_category_income):
        """Test transaction type must match category type"""
        # Income category with expense transaction type should fail
        transaction_data = {
            "entity_id": test_entity.id,
            "category_id": test_category_income.id,
            "transaction_type": "expense",  # Mismatched!
            "amount": 5000,
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": datetime.now().isoformat(),
        }
        
        response = client.post(
            "/transactions/",
            json=transaction_data,
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "type" in response.json()["detail"]
    
    def test_create_transaction_entity_not_found(self, client, test_user_headers, test_category_income):
        """Test creating transaction with non-existent entity"""
        transaction_data = {
            "entity_id": 9999,
            "category_id": test_category_income.id,
            "transaction_type": "income",
            "amount": 5000,
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": datetime.now().isoformat(),
        }
        
        response = client.post(
            "/transactions/",
            json=transaction_data,
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_transaction_category_not_found(self, client, test_user_headers, test_entity):
        """Test creating transaction with non-existent category"""
        transaction_data = {
            "entity_id": test_entity.id,
            "category_id": 9999,
            "transaction_type": "income",
            "amount": 5000,
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": datetime.now().isoformat(),
        }
        
        response = client.post(
            "/transactions/",
            json=transaction_data,
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_transaction_unauthorized_entity(self, client, test_db, test_user):
        """Test creating transaction on someone else's entity"""
        from auth import hash_password, create_access_token
        from models import User, Entity, TransactionCategory
        
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
        
        # Create category
        category = TransactionCategory(
            name="Salary",
            description="Salary",
            type=TransactionType.INCOME,
        )
        test_db.add(category)
        test_db.commit()
        
        transaction_data = {
            "entity_id": other_entity.id,
            "category_id": category.id,
            "transaction_type": "income",
            "amount": 5000,
            "category": "Salary",
            "description": "Monthly salary",
            "transaction_date": datetime.now().isoformat(),
        }
        
        token = create_access_token(test_user.id, test_user.email, test_user.role)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/transactions/", json=transaction_data, headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListTransactions:
    """Tests for listing transactions"""
    
    def test_list_transactions_success(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income):
        """Test successfully listing transactions"""
        # Create a few transactions
        for i in range(3):
            transaction = Transaction(
                owner_id=test_user.id,
                entity_id=test_entity.id,
                category_id=test_category_income.id,
                transaction_type=TransactionType.INCOME,
                amount=1000 * (i + 1),
                category_name="Income",
                description=f"Transaction {i + 1}",
                transaction_date=datetime.now(),
            )
            test_db.add(transaction)
        test_db.commit()
        
        response = client.get(
            f"/transactions/?entity_id={test_entity.id}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
    
    def test_list_transactions_filter_by_type(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income, test_category_expense):
        """Test filtering transactions by type"""
        # Create income transactions
        for i in range(2):
            income = Transaction(
                owner_id=test_user.id,
                entity_id=test_entity.id,
                category_id=test_category_income.id,
                transaction_type=TransactionType.INCOME,
                amount=1000,
                category_name="Income",
                transaction_date=datetime.now(),
            )
            test_db.add(income)
        
        # Create expense transactions
        for i in range(1):
            expense = Transaction(
                owner_id=test_user.id,
                entity_id=test_entity.id,
                category_id=test_category_expense.id,
                transaction_type=TransactionType.EXPENSE,
                amount=500,
                category_name="Expense",
                transaction_date=datetime.now(),
            )
            test_db.add(expense)
        test_db.commit()
        
        response = client.get(
            f"/transactions/?entity_id={test_entity.id}&type=income",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(t["transaction_type"] == "income" for t in data)
    
    def test_list_transactions_filter_by_date_range(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income):
        """Test filtering transactions by date range"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        # Create transaction yesterday
        past_trans = Transaction(
            owner_id=test_user.id,
            entity_id=test_entity.id,
            category_id=test_category_income.id,
            transaction_type=TransactionType.INCOME,
            amount=1000,
            category_name="Income",
            transaction_date=yesterday,
        )
        test_db.add(past_trans)
        
        # Create transaction today
        today_trans = Transaction(
            owner_id=test_user.id,
            entity_id=test_entity.id,
            category_id=test_category_income.id,
            transaction_type=TransactionType.INCOME,
            amount=2000,
            category_name="Income",
            transaction_date=now,
        )
        test_db.add(today_trans)
        test_db.commit()
        
        response = client.get(
            f"/transactions/?entity_id={test_entity.id}&date_from={now.isoformat()}&date_to={tomorrow.isoformat()}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1


class TestGetTransaction:
    """Tests for retrieving single transaction"""
    
    def test_get_transaction_success(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income):
        """Test successfully retrieving a transaction"""
        transaction = Transaction(
            owner_id=test_user.id,
            entity_id=test_entity.id,
            category_id=test_category_income.id,
            transaction_type=TransactionType.INCOME,
            amount=5000,
            category_name="Salary",
            description="Monthly salary",
            transaction_date=datetime.now(),
        )
        test_db.add(transaction)
        test_db.commit()
        
        response = client.get(
            f"/transactions/{transaction.id}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == transaction.id
        assert data["amount"] == 5000
    
    def test_get_transaction_not_found(self, client, test_user_headers):
        """Test getting non-existent transaction"""
        response = client.get(
            "/transactions/9999",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateTransaction:
    """Tests for updating transactions"""
    
    def test_update_transaction_success(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income):
        """Test successfully updating a transaction"""
        transaction = Transaction(
            owner_id=test_user.id,
            entity_id=test_entity.id,
            category_id=test_category_income.id,
            transaction_type=TransactionType.INCOME,
            amount=5000,
            category_name="Salary",
            description="Monthly salary",
            transaction_date=datetime.now(),
        )
        test_db.add(transaction)
        test_db.commit()
        
        update_data = {
            "amount": 6000,
            "description": "Updated salary",
        }
        
        response = client.put(
            f"/transactions/{transaction.id}",
            json=update_data,
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["amount"] == 6000
        assert data["description"] == "Updated salary"
    
    def test_update_transaction_not_found(self, client, test_user_headers):
        """Test updating non-existent transaction"""
        update_data = {"amount": 6000}
        
        response = client.put(
            "/transactions/9999",
            json=update_data,
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteTransaction:
    """Tests for deleting transactions"""
    
    def test_delete_transaction_success(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income):
        """Test successfully deleting a transaction"""
        transaction = Transaction(
            owner_id=test_user.id,
            entity_id=test_entity.id,
            category_id=test_category_income.id,
            transaction_type=TransactionType.INCOME,
            amount=5000,
            category_name="Salary",
            description="Monthly salary",
            transaction_date=datetime.now(),
        )
        test_db.add(transaction)
        test_db.commit()
        transaction_id = transaction.id
        
        response = client.delete(
            f"/transactions/{transaction_id}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        deleted = test_db.query(Transaction).filter(Transaction.id == transaction_id).first()
        assert deleted is None
    
    def test_delete_transaction_not_found(self, client, test_user_headers):
        """Test deleting non-existent transaction"""
        response = client.delete(
            "/transactions/9999",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
