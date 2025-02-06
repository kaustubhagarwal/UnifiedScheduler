from enum import Enum

class AccountType(Enum):
    BANK = "Bank Account"
    CREDIT = "Credit Card"
    CASH = "Cash"
    INVESTMENT = "Investment"
    OTHER = "Other"

class TransactionType(Enum):
    INCOME = "Income"
    EXPENSE = "Expense"
    TRANSFER = "Transfer"
