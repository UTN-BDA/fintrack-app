from flask import Blueprint, request
from marshmallow import ValidationError
from app.services import TransactionService, ResponseBuilder
from app.mapping import TransactionSchema, ResponseSchema

transaction_bp = Blueprint('transactions', __name__)

response_schema = ResponseSchema()
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)
transaction_service = TransactionService()

@transaction_bp.route('', methods=['POST'])
def create_transaction():
    builder = ResponseBuilder()
    try:
        transaction = transaction_schema.load(request.json or {})
        created = transaction_service.create_transaction(
            user_id=transaction.user_id,
            amount=transaction.amount,
            date=transaction.date,
            description=transaction.description,
            method=transaction.method,
            is_income=transaction.is_income,
            category_id=transaction.category_id
        )
        data = transaction_schema.dump(created)
        builder.add_message("Transacción creada correctamente").add_status_code(201).add_data(data)
        return response_schema.dump(builder.build()), 201

    except ValidationError as err:
        builder.add_message("Error de validación").add_status_code(422).add_data(err.messages)
        return response_schema.dump(builder.build()), 422

@transaction_bp.route('', methods=['GET'])
def list_transactions():
    builder = ResponseBuilder()
    # filtros opcionales
    user_id     = request.args.get('user_id', type=int)
    start_date  = request.args.get('start_date')   # formato YYYY-MM-DD
    end_date    = request.args.get('end_date')
    is_income   = request.args.get('is_income', type=lambda v: v.lower()=='true')
    category_id = request.args.get('category_id', type=int)
    page        = request.args.get('page', default=1,  type=int)
    per_page    = request.args.get('per_page', default=20, type=int)

    if any([start_date, end_date, is_income is not None, category_id]):
        transactions = transaction_service.filter_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            is_income=is_income,
            category_id=category_id,
            page=page,
            per_page=per_page
        )
    else:
        transactions = transaction_service.list_transactions(
            user_id=user_id,
            page=page,
            per_page=per_page
        )

    data = transactions_schema.dump(transactions)
    builder.add_message("Listado de transacciones").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200

@transaction_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    builder = ResponseBuilder()
    transaction = transaction_service.get_transaction(transaction_id)
    if not transaction:
        builder.add_message("Transacción no encontrada").add_status_code(404)
        return response_schema.dump(builder.build()), 404

    data = transaction_schema.dump(transaction)
    builder.add_message("Transacción encontrada").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200

@transaction_bp.route('/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    builder = ResponseBuilder()
    try:
        updates = transaction_schema.load(request.json or {}, partial=True)
    except ValidationError as err:
        builder.add_message("Error de validación").add_status_code(422).add_data(err.messages)
        return response_schema.dump(builder.build()), 422

    data = {}
    for field in ('amount', 'date', 'description', 'method', 'is_income', 'category_id'):
        val = getattr(updates, field, None)
        if val is not None:
            data[field] = val

    updated = transaction_service.update_transaction(transaction_id, **data)
    if updated is None:
        builder.add_message("Transacción no encontrada o sin cambios").add_status_code(404)
        return response_schema.dump(builder.build()), 404

    result = transaction_schema.dump(updated)
    builder.add_message("Transacción actualizada").add_status_code(200).add_data(result)
    return response_schema.dump(builder.build()), 200

@transaction_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    builder = ResponseBuilder()
    success = transaction_service.delete_transaction(transaction_id, soft=True)
    if not success:
        builder.add_message("Transacción no encontrada").add_status_code(404)
        return response_schema.dump(builder.build()), 404

    builder.add_message("Transacción eliminada").add_status_code(204)
    return response_schema.dump(builder.build()), 204

@transaction_bp.route('/<int:transaction_id>/restore', methods=['PATCH'])
def restore_transaction(transaction_id):
    builder = ResponseBuilder()
    restored = transaction_service.restore_transaction(transaction_id)
    if not restored:
        builder.add_message("Transacción no encontrada o no eliminada").add_status_code(404)
        return response_schema.dump(builder.build()), 404

    data = transaction_schema.dump(restored)
    builder.add_message("Transacción restaurada").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200
