from typing import List
from app import db
from app.models import Transaction

class TransactionRepository:
    """
    Repository for Transaction entity (Single Responsibility Principle).
    """

    def save(self, transaction: Transaction) -> Transaction:
        db.session.add(transaction)
        db.session.commit()
        return transaction

    def update(self, transaction: Transaction, id: int) -> Transaction:
        entity = self.find(id)
        if entity is None:
            return None

        entity.amount = transaction.amount
        entity.date = transaction.date
        entity.description = transaction.description
        entity.method = transaction.method
        entity.is_income = transaction.is_income
        entity.deleted = transaction.deleted
        entity.user_id = transaction.user_id
        entity.category_id = transaction.category_id

        db.session.add(entity)
        db.session.commit()
        return entity

    def delete(self, transaction: Transaction) -> None:
        db.session.delete(transaction)
        db.session.commit()

    def all(self) -> List[Transaction]:
        return db.session.query(Transaction).all()

    def find(self, id: int) -> Transaction:
        if id is None or id == 0:
            return None
        try:
            return db.session.query(Transaction).filter(Transaction.id == id).one()
        except:
            return None

    def find_by_user(self, user_id: int) -> List[Transaction]:
        return db.session.query(Transaction).filter(Transaction.user_id == user_id).all()
