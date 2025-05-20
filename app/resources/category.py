from flask import Blueprint, request
from marshmallow import ValidationError
from app.services import CategoryService, ResponseBuilder
from app.mapping import CategorySchema, ResponseSchema

category_bp = Blueprint('categories', __name__)
service = CategoryService()
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
response_schema = ResponseSchema()

@category_bp.route('', methods=['POST'])
def create_category():
    builder = ResponseBuilder()
    try:
        # Validación y deserialización
        c = category_schema.load(request.json or {})
        # Guardado mediante el repositorio
        created = service.repo.save(c)
        data = category_schema.dump(created)
        # Construcción de respuesta exitosa
        builder.add_message("Categoría creada correctamente").add_status_code(201).add_data(data)
        return response_schema.dump(builder.build()), 201

    except ValidationError as err:
        # Error de validación
        builder.add_message("Error de validación").add_status_code(422).add_data(err.messages)
        return response_schema.dump(builder.build()), 422

@category_bp.route('', methods=['GET'])
def list_categories():
    builder = ResponseBuilder()
    favorites = request.args.get('favorites_only', 'false').lower() == 'true'
    recurring = request.args.get('recurring_only', 'false').lower() == 'true'
    cats = service.list_categories(favorites_only=favorites, recurring_only=recurring)
    data = categories_schema.dump(cats)
    builder.add_message("Listado de categorías").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200

@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    builder = ResponseBuilder()
    cat = service.get_category(category_id)
    if not cat:
        builder.add_message("Categoría no encontrada").add_status_code(404)
        return response_schema.dump(builder.build()), 404
    data = category_schema.dump(cat)
    builder.add_message("Categoría obtenida").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200

@category_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    builder = ResponseBuilder()
    try:
        updates = category_schema.load(request.json or {}, partial=True)
    except ValidationError as err:
        builder.add_message("Error de validación").add_status_code(422).add_data(err.messages)
        return response_schema.dump(builder.build()), 422

    updated = service.update_category(category_id, **updates.__dict__)
    if not updated:
        builder.add_message("Categoría no encontrada o sin cambios").add_status_code(404)
        return response_schema.dump(builder.build()), 404
    data = category_schema.dump(updated)
    builder.add_message("Categoría actualizada correctamente").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200

@category_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    builder = ResponseBuilder()
    success = service.delete_category(category_id, soft=True)
    if not success:
        builder.add_message("Categoría no encontrada").add_status_code(404)
        return response_schema.dump(builder.build()), 404
    builder.add_message("Categoría eliminada correctamente").add_status_code(204)
    return response_schema.dump(builder.build()), 204

@category_bp.route('/<int:category_id>/favorite', methods=['PATCH'])
def toggle_favorite(category_id):
    builder = ResponseBuilder()
    cat = service.get_category(category_id)
    if not cat:
        builder.add_message("Categoría no encontrada").add_status_code(404)
        return response_schema.dump(builder.build()), 404
    updated = service.update_category(category_id, is_favorite=not cat.is_favorite)
    data = category_schema.dump(updated)
    builder.add_message("Estado de favorito modificado").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200

@category_bp.route('/<int:category_id>/recurring', methods=['PATCH'])
def toggle_recurring(category_id):
    builder = ResponseBuilder()
    cat = service.get_category(category_id)
    if not cat:
        builder.add_message("Categoría no encontrada").add_status_code(404)
        return response_schema.dump(builder.build()), 404
    updated = service.update_category(category_id, is_recurring=not cat.is_recurring)
    data = category_schema.dump(updated)
    builder.add_message("Estado de recurrencia modificado").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200
