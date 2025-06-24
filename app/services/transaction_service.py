import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional
from datetime import date
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from uuid import uuid4
import redis
from app.models import Transaction
from app.repository.transaction_repository import TransactionRepository

basedir = os.path.abspath(Path(__file__).parents[2])
load_dotenv(os.path.join(basedir, '.env'))

class TransactionService:
    def __init__(self, repo: TransactionRepository = None):
        self.repo = repo or TransactionRepository()
        self.redis_client = redis.StrictRedis(
            host=os.environ.get('REDIS_HOST'),
            port=int(os.environ.get('REDIS_PORT')),
            db=int(os.environ.get('REDIS_DB')),
            password=os.environ.get('REDIS_PASSWORD'),
        )

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
    
    def generate_graph(self, user_id: int) -> str:
        """
        Genera un gráfico tipo dona de los gastos por categoría para un usuario,
        lo guarda en Redis como un objeto binario y devuelve la URL para acceder a la imagen.
        """
        if not user_id:
            raise ValueError("El user_id no puede ser None")
        
        matplotlib.use('Agg')
        amounts, labels = self.repo.generate_graph(user_id)

        if not amounts:
            raise ValueError("No hay datos para generar el gráfico")

        colors = [
            "#A28DFF", "#91E3A5", "#FFDC7D", "#FF9139",
            "#00FFA3", "#FFD6E0", "#96D3F5", "#FF6A6A"
        ][:len(amounts)]

        fig, ax = plt.subplots(figsize=(6, 6), dpi=100)

        wedges, _ = ax.pie(
            amounts,
            labels=None,
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor='white'),
            colors=colors
        )

        legend_labels = [f"{label}  ${int(amount)}" for label, amount in zip(labels, amounts)]

        ax.legend(
            wedges,
            legend_labels,
            title="Categorías",
            loc='lower center',
            bbox_to_anchor=(0.5, -0.15),
            ncol=2,
            frameon=False,
            fontsize=10
        )

        buffer = BytesIO()
        try:
            plt.savefig(buffer, format='png', transparent=True, bbox_inches='tight')
            buffer.seek(0)
            image_data = buffer.getvalue()
            buffer.close()

            # Generar un identificador único para la imagen
            image_key = f"donut_chart_user_{user_id}_{uuid4().hex}"

            # Guardar la imagen en Redis con un TTL de 300 segundos (5 minutos)
            self.redis_client.setex(image_key, 300, image_data)

            print("✅ Imagen guardada en Redis con clave:", image_key)
        except Exception as e:
            print("❌ Error al guardar imagen en Redis:", e)
            raise e
        finally:
            plt.close()

        # Devolver la URL para acceder a la imagen
        return f"/transactions/images/{image_key}"
