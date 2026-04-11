"""
Integration and unit tests for reports routes
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status

from models import Transaction, TransactionType


class TestGenerateReport:
    """Tests for generating financial reports"""
    
    def test_generate_report_success(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income, test_category_expense):
        """Test successfully generating a report"""
        # Create income and expense transactions
        income_trans = Transaction(
            owner_id=test_user.id,
            entity_id=test_entity.id,
            category_id=test_category_income.id,
            transaction_type=TransactionType.INCOME,
            amount=5000,
            category_name="Salary",
            transaction_date=datetime.now(),
        )
        test_db.add(income_trans)
        
        expense_trans = Transaction(
            owner_id=test_user.id,
            entity_id=test_entity.id,
            category_id=test_category_expense.id,
            transaction_type=TransactionType.EXPENSE,
            amount=1000,
            category_name="Groceries",
            transaction_date=datetime.now(),
        )
        test_db.add(expense_trans)
        test_db.commit()
        
        response = client.get(
            f"/reports/?entity_id={test_entity.id}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["entity_id"] == test_entity.id
        assert data["entity_name"] == test_entity.name
        assert data["total_income"] == 5000.0
        assert data["total_expenses"] == 1000.0
        assert data["net_balance"] == 4000.0
    
    def test_generate_report_with_date_range(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income):
        """Test generating report with date range filter"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        # Create transaction yesterday (outside range)
        past_trans = Transaction(
            owner_id=test_user.id,
            entity_id=test_entity.id,
            category_id=test_category_income.id,
            transaction_type=TransactionType.INCOME,
            amount=1000,
            category_name="Salary",
            transaction_date=yesterday,
        )
        test_db.add(past_trans)
        
        # Create transaction today (inside range)
        today_trans = Transaction(
            owner_id=test_user.id,
            entity_id=test_entity.id,
            category_id=test_category_income.id,
            transaction_type=TransactionType.INCOME,
            amount=2000,
            category_name="Salary",
            transaction_date=now,
        )
        test_db.add(today_trans)
        test_db.commit()
        
        response = client.get(
            f"/reports/?entity_id={test_entity.id}&date_from={now.isoformat()}&date_to={tomorrow.isoformat()}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should only include today's transaction
        assert data["total_income"] == 2000.0
    
    def test_generate_report_empty(self, client, test_user_headers, test_entity):
        """Test generating report for entity with no transactions"""
        response = client.get(
            f"/reports/?entity_id={test_entity.id}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_income"] == 0.0
        assert data["total_expenses"] == 0.0
        assert data["net_balance"] == 0.0
        assert len(data["income_breakdown"]) == 0
        assert len(data["expense_breakdown"]) == 0
    
    def test_generate_report_entity_not_found(self, client, test_user_headers):
        """Test generating report for non-existent entity"""
        response = client.get(
            "/reports/?entity_id=9999",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_generate_report_unauthorized(self, client, test_user_headers, test_db):
        """Test generating report for other user's entity"""
        from auth import hash_password, create_access_token
        from models import User, Entity
        
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
        
        response = client.get(
            f"/reports/?entity_id={other_entity.id}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_generate_report_category_breakdown(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income):
        """Test that report includes category breakdown"""
        # Create multiple transactions in same category
        for amount in [1000, 2000, 3000]:
            trans = Transaction(
                owner_id=test_user.id,
                entity_id=test_entity.id,
                category_id=test_category_income.id,
                transaction_type=TransactionType.INCOME,
                amount=amount,
                category_name="Salary",
                transaction_date=datetime.now(),
            )
            test_db.add(trans)
        test_db.commit()
        
        response = client.get(
            f"/reports/?entity_id={test_entity.id}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["income_breakdown"]) == 1
        assert data["income_breakdown"][0]["category_name"] == "Salary"
        assert data["income_breakdown"][0]["total"] == 6000.0
        assert data["income_breakdown"][0]["transaction_count"] == 3
    
    def test_generate_report_breakdown_sorted_by_amount(self, client, test_user_headers, test_db, test_user, test_entity, test_category_income, test_category_expense):
        """Test that breakdown is sorted by amount (highest first)"""
        from models import TransactionCategory
        
        # Create multiple expense categories
        groceries = test_category_expense
        utilities = TransactionCategory(
            name="Utilities",
            description="Utility bills",
            type=TransactionType.EXPENSE,
        )
        test_db.add(utilities)
        test_db.commit()
        
        # Add expense transactions
        for category, amount in [(groceries, 1000), (utilities, 5000)]:
            trans = Transaction(
                owner_id=test_user.id,
                entity_id=test_entity.id,
                category_id=category.id,
                transaction_type=TransactionType.EXPENSE,
                amount=amount,
                category_name=category.name,
                transaction_date=datetime.now(),
            )
            test_db.add(trans)
        test_db.commit()
        
        response = client.get(
            f"/reports/?entity_id={test_entity.id}",
            headers=test_user_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should be sorted by amount descending
        assert data["expense_breakdown"][0]["total"] == 5000.0
        assert data["expense_breakdown"][1]["total"] == 1000.0
    
    def test_generate_report_unauthorized_no_auth(self, client):
        """Test generating report without authentication"""
        response = client.get("/reports/?entity_id=1")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
