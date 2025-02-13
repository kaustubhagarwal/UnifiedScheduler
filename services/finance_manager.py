from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models.database import Account, Transaction, Category, AccountType, TransactionType, get_db
from sqlalchemy import func

class FinanceManager:
    def __init__(self):
        self.db = next(get_db())

    def add_account(self, name: str, account_type: str, initial_balance: float = 0.0,
                   currency: str = "USD", description: str = None) -> None:
        """Add a new financial account"""
        new_account = Account(
            id=str(uuid.uuid4()),
            name=name,
            type=AccountType(account_type),
            balance=initial_balance,
            currency=currency,
            description=description
        )
        self.db.add(new_account)
        self.db.commit()

    def add_category(self, name: str, color: str, description: str = None) -> None:
        """Add a new transaction category"""
        new_category = Category(
            id=str(uuid.uuid4()),
            name=name,
            color=color,
            description=description
        )
        self.db.add(new_category)
        self.db.commit()

    def add_transaction(self, account_id: str, category_id: str, 
                       transaction_type: str, amount: float,
                       description: str = None, date: datetime = None) -> None:
        """Add a new transaction and update account balance"""
        # Get the account
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise ValueError("Account not found")

        # Calculate balance change based on transaction type
        if transaction_type == TransactionType.EXPENSE.value:
            account.balance -= amount
            amount = -amount  # Store expenses as negative values
        elif transaction_type == TransactionType.INCOME.value:
            account.balance += amount

        new_transaction = Transaction(
            id=str(uuid.uuid4()),
            account_id=account_id,
            category_id=category_id,
            type=TransactionType(transaction_type),
            amount=amount,
            description=description,
            date=date or datetime.now()
        )
        self.db.add(new_transaction)
        self.db.commit()

    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts"""
        accounts = self.db.query(Account).all()
        return [{
            'id': acc.id,
            'name': acc.name,
            'type': acc.type.value,
            'balance': acc.balance,
            'currency': acc.currency,
            'description': acc.description,
            'created_at': acc.created_at.isoformat()
        } for acc in accounts]

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        categories = self.db.query(Category).all()
        return [{
            'id': cat.id,
            'name': cat.name,
            'color': cat.color,
            'description': cat.description
        } for cat in categories]

    def get_transactions(self, account_id: Optional[str] = None,
                        category_id: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get transactions with optional filters"""
        query = self.db.query(Transaction)

        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        transactions = query.order_by(Transaction.date.desc()).all()
        return [{
            'id': tx.id,
            'account': tx.account.name,
            'category': tx.category.name,
            'type': tx.type.value,
            'amount': abs(tx.amount),  # Convert back to positive for display
            'description': tx.description,
            'date': tx.date.isoformat(),
            'category_color': tx.category.color
        } for tx in transactions]

    def get_net_worth(self) -> float:
        """Calculate total net worth across all accounts"""
        accounts = self.db.query(Account).all()
        return sum(account.balance for account in accounts)

    def get_spending_by_category(self, start_date: datetime = None,
                               end_date: datetime = None) -> List[Dict[str, Any]]:
        """Get spending summary grouped by category"""
        query = self.db.query(
            Category.name,
            Category.color,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).group_by(Category.name, Category.color)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        results = query.all()
        return [{
            'category': result[0],
            'color': result[1],
            'total': abs(result[2])
        } for result in results]
    
    def delete_account(self, account_id: str) -> bool:
        """Delete an account and its associated transactions"""
        # Fetch the account
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account:
            return False  # Account not found

        # Delete all transactions associated with the account
        self.db.query(Transaction).filter(Transaction.account_id == account_id).delete()

        # Delete the account itself
        self.db.delete(account)
        self.db.commit()
        return True