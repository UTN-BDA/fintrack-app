import csv
import io
from typing import List
from app.models.transaction import Transaction

def export_transactions_to_csv(transactions: List[Transaction]) -> bytes:
    """
    Recibe una lista de instancias Transaction y devuelve un archivo CSV en bytes.
    Columnas: id, user_id, amount, date, description, method, is_income, category_id, deleted
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Encabezados
    writer.writerow([
        "amount",
        "date",
        "description",
        "method",
        "is_income",
        "category_id",
        "deleted"
    ])

    # Filas
    for txn in transactions:
        writer.writerow([
            float(txn.amount),
            txn.date.isoformat() if txn.date else "",
            txn.description or "",
            txn.method or "",
            txn.is_income,
            txn.category_id if txn.category_id is not None else "",
            txn.deleted
        ])

    # Obtener bytes
    csv_data = output.getvalue().encode('utf-8')
    output.close()
    return csv_data
