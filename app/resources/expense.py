from flask import Blueprint, request
from app.services import ExpenseService, ResponseBuilder
from app.mapping import ResponseSchema
from datetime import datetime
from marshmallow import ValidationError

expense_bp = Blueprint('expenses', __name__)

expense_service = ExpenseService()
response_schema = ResponseSchema()

@expense_bp.route('/total_by_period', methods=['GET'])
def total_by_period():
    builder = ResponseBuilder()
    try:
        # Validar y parsear parámetros
        start = request.args.get('start')
        end = request.args.get('end')
        user_id = request.args.get('user_id', type=int)
        is_income = request.args.get('is_income', type=lambda v: v.lower() == 'true')
        if not start or not end:
            raise ValidationError("Los parámetros 'start' y 'end' son obligatorios.")
        
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()

        # Llamar al servicio
        total = expense_service.total_by_period(user_id=user_id, is_income=is_income, start=start_date, end=end_date)
        builder.add_message("Total calculado correctamente").add_status_code(200).add_data({"total": total})
        return response_schema.dump(builder.build()), 200

    except ValidationError as err:
        builder.add_message("Error de validación").add_status_code(422).add_data({"error": str(err)})
        return response_schema.dump(builder.build()), 422

@expense_bp.route('/compare_months', methods=['GET'])
def compare_months():
    builder = ResponseBuilder()
    try:
        # Validar y parsear parámetros
        month1 = request.args.get('month1')
        month2 = request.args.get('month2')
        user_id = request.args.get('user_id', type=int)
        is_income = request.args.get('is_income', type=lambda v: v.lower() == 'true')
        if not month1 or not month2:
            raise ValidationError("Los parámetros 'month1' y 'month2' son obligatorios.")
        
        month1_date = datetime.strptime(month1, "%Y-%m")
        month2_date = datetime.strptime(month2, "%Y-%m")

        # Llamar al servicio
        comparison = expense_service.compare_months(user_id=user_id, is_income=is_income, month1=month1_date, month2=month2_date)
        builder.add_message("Comparación realizada correctamente").add_status_code(200).add_data(comparison)
        return response_schema.dump(builder.build()), 200

    except ValidationError as err:
        builder.add_message("Error de validación").add_status_code(422).add_data({"error": str(err)})
        return response_schema.dump(builder.build()), 422

@expense_bp.route('/key_indicators', methods=['GET'])
def key_indicators():
    builder = ResponseBuilder()
    try:
        # Validar y parsear parámetros
        start = request.args.get('start')
        end = request.args.get('end')
        user_id = request.args.get('user_id', type=int)
        is_income = request.args.get('is_income', type=lambda v: v.lower() == 'true')
        if not start or not end:
            raise ValidationError("Los parámetros 'start' y 'end' son obligatorios.")
        
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()

        # Llamar al servicio
        indicators = expense_service.key_indicators(user_id=user_id, is_income=is_income, start=start_date, end=end_date)
        builder.add_message("Indicadores calculados correctamente").add_status_code(200).add_data(indicators)
        return response_schema.dump(builder.build()), 200

    except ValidationError as err:
        builder.add_message("Error de validación").add_status_code(422).add_data({"error": str(err)})
        return response_schema.dump(builder.build()), 422
