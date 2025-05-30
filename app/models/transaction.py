from sqlalchemy import Index, text
from app.extensions import db

class Transaction(db.Model):
    __tablename__ = 'transaction'
    __table_args__ = (
        # Para listar rápido transacciones de un usuario
        Index('ix_txn_user', 'user_id'),
        # Para listar rápido transacciones de un usuario por fecha
        Index('ix_txn_user_date', 'user_id', 'date'),
        # Búsquedas por categoría
        Index('ix_txn_category', 'category_id'),
        # Si filtras mucho por tipo ingreso/egreso
        Index('ix_txn_income', 'is_income'),
        # Para excluir las transacciones borradas de forma ultra‑rápida sin tocar todas las filas (Postgres partial index)
        Index(
            'ix_txn_active',
            'id',
            postgresql_where=text('deleted = false')
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255))
    method = db.Column(db.String(50))
    is_income = db.Column(db.Boolean, nullable=False, default=False)
    deleted = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    user = db.relationship('User', back_populates='transactions')
    category = db.relationship('Category', back_populates='transactions')