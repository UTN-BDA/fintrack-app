# services/transaction_service.py
from typing import List, Optional
from datetime import date
from app.models import Transaction
from app.repository.transaction_repository import TransactionRepository

class TransactionService:
    def __init__(self, repo: TransactionRepository = None):
        self.repo = repo or TransactionRepository()

    def create_transaction(
        self,
        user_id: int,
        amount: float,
        date: date,
        description: str = None,
        method: str = None,
        is_income: bool = False,
        category_id: int = None
    ) -> Transaction:
        """Crea una nueva transacción"""
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            date=date,
            description=description,
            method=method,
            is_income=is_income,
            category_id=category_id
        )
        return self.repo.save(transaction)

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Obtiene una transacción por su ID"""
        return self.repo.get_by_id(transaction_id)

    def list_transactions(
        self,
        user_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[Transaction]:
        """Lista transacciones (global o de un usuario)"""
        if user_id:
            return self.repo.get_by_user(user_id, page=page, per_page=per_page)
        return self.repo.get_all(page=page, per_page=per_page)

    def filter_transactions(
        self,
        user_id: int,
        start_date: date = None,
        end_date: date = None,
        is_income: bool = None,
        category_id: int = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[Transaction]:
        """Lista transacciones filtradas para un usuario"""
        return self.repo.filter(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            is_income=is_income,
            category_id=category_id,
            page=page,
            per_page=per_page
        )

    def update_transaction(
        self,
        transaction_id: int,
        **updates
    ) -> Optional[Transaction]:
        """Actualiza campos de una transacción existente"""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return None
        # Solo campos válidos:
        allowed = {"amount", "date", "description", "method", "is_income", "category_id"}
        data = {k: v for k, v in updates.items() if k in allowed}
        if not data:
            return transaction
        return self.repo.update(transaction, **data)

    def delete_transaction(self, transaction_id: int, soft: bool = True) -> bool:
        """Elimina o marca transacción como borrada. Por defecto hace soft-delete"""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return False
        if soft:
            self.repo.soft_delete(transaction)
        else:
            self.repo.delete(transaction)
        return True

    def restore_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Restaura una transacción borrada (solo si existe)"""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return None
        return self.repo.restore(transaction)
