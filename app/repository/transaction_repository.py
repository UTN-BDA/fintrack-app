from typing import List, Optional
from datetime import date
from app import db
from app.models import Transaction

class TransactionRepository:

    def save(self, transaction: Transaction) -> Transaction:
        """Inserta o actualiza una transacción"""
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Devuelve una transacción por su ID (incluye borradas)"""
        return Transaction.query.get(transaction_id)
    
    def get_all(self, page: int = 1, per_page: int = 20) -> List[Transaction]:
        """Lista todas las transacciones no eliminadas, paginadas"""
        pag = Transaction.query.filter_by(deleted=False).order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return pag.items
    
    def get_by_user(self, user_id: int, page: int = 1, per_page: int = 20) -> List[Transaction]:
        """Lista transacciones de un usuario, no eliminadas, paginadas"""
        pag = Transaction.query.filter_by(user_id=user_id, deleted=False).order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return pag.items
    
    def filter(
        self,
        user_id: Optional[int] = None,
        start_date: date = None,
        end_date: date = None,
        is_income: bool = None,
        category_id: int = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[Transaction]:
        """Filtra por rango de fechas, tipo y categoría"""
        q = Transaction.query.filter_by(deleted=False)

        if user_id is not None:
            q = q.filter_by(user_id=user_id)
        if start_date:
            q = q.filter(Transaction.date >= start_date)
        if end_date:
            q = q.filter(Transaction.date <= end_date)
        if is_income is not None:
            q = q.filter_by(is_income=is_income)
        if category_id:
            q = q.filter_by(category_id=category_id)
        pag = q.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return pag.items

    def update(self, transaction: Transaction, **kwargs) -> Transaction:
        """Actualiza campos de la transacción"""
        for attr, val in kwargs.items():
            setattr(transaction, attr, val)
        db.session.commit()
        return transaction

    def delete(self, transaction: Transaction) -> None:
        """Elimina físicamente la transacción"""
        db.session.delete(transaction)
        db.session.commit()

    def soft_delete(self, transaction: Transaction) -> Transaction:
        """Marca la transacción como eliminada (deleted=True)"""
        transaction.deleted = True
        db.session.commit()
        return transaction

    def restore(self, transaction: Transaction) -> Transaction:
        """Restaura una transacción borrada (deleted=False)"""
        transaction.deleted = False
        db.session.commit()
        return transaction
