from typing import Optional
from datetime import date, datetime, timedelta
from typing import Dict, Any
from app.repository.transaction_repository import TransactionRepository

class ExpenseService:
    def __init__(self, repo: TransactionRepository = None):
        self.repo = repo or TransactionRepository()

    def total_by_period(self, user_id: int = None, is_income: bool = None, start: date = None, end: date = None) -> float:
        """Suma todos los montos (ingresos negativos o solo egresos, según convenga) entre start y end inclusive"""
        transaction = self.repo.filter(
            user_id=user_id,
            is_income=is_income,
            start_date=start,
            end_date=end,
            page=1,
            per_page=10**6  # tomar todos
        )
        return sum(txn.amount for txn in transaction)

    def compare_months(self, user_id: int = None, is_income: bool = None, month1: datetime = None, month2: datetime = None) -> Dict[str, Any]:
        """Compara el total de dos meses. Retorna {'month1_total', 'month2_total', 'percent_change'}"""
        def month_range(dt: datetime):
            first = dt.replace(day=1)
            next_month = (first + timedelta(days=32)).replace(day=1)
            last = next_month - timedelta(days=1)
            return first.date(), last.date()

        s1, e1 = month_range(month1)
        s2, e2 = month_range(month2)

        total1 = self.total_by_period(user_id=user_id, is_income=is_income, start=s1, end=e1)
        total2 = self.total_by_period(user_id=user_id, is_income=is_income, start=s2, end=e2)

        percent = ((total2 - total1) / total1 * 100) if total1 else None
        return {
            "mes1": month1.strftime("%Y-%m"),
            "mes1_total": total1,
            "mes2": month2.strftime("%Y-%m"),
            "mes2_total": total2,
            "Porcentaje_de_cambio": percent
        }

    def key_indicators(self, user_id: int = None, is_income: bool = None, start: date = None, end: date = None) -> Dict[str, Any]:
        """Promedio diario, máximo y mínimo de gasto/ingreso en el periodo [start, end]"""
        transaction = self.repo.filter(
            user_id=user_id,
            is_income=is_income,
            start_date=start,
            end_date=end,
            page=1,
            per_page=10**6
        )
        amounts = [txn.amount for txn in transaction]
        days = (end - start).days + 1
        return {
            "promedio_diario": float(sum(amounts) / days) if days else 0,
            "suma_maxima": max(amounts) if amounts else 0,
            "Suma_minima": min(amounts) if amounts else 0
        }
