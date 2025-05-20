from flask import Blueprint, request
from marshmallow import ValidationError
from app.services import UserService, ResponseBuilder
from app.mapping import UserSchema, ResponseSchema

user_bp = Blueprint('users', __name__)

response_schema = ResponseSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_service = UserService()

@user_bp.route('', methods=['POST'])
def create_user():
    builder = ResponseBuilder()
    try:
        # Validación y deserialización
        u = user_schema.load(request.json or {})
        # Llamada al servicio
        created = user_service.create_user(
            username=u.username,
            email=u.email,
            password=u.password_hash
        )
        data = user_schema.dump(created)
        # ResponseBuilder para éxito
        builder.add_message("Usuario creado correctamente").add_status_code(201).add_data(data)
        return response_schema.dump(builder.build()), 201

    except ValidationError as err:
        # ResponseBuilder para error de validación
        builder.add_message("Error de validación").add_status_code(422).add_data(err.messages)
        return response_schema.dump(builder.build()), 422

@user_bp.route('', methods=['GET'])
def list_users():
    builder = ResponseBuilder()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    users = user_service.list_users(page=page, per_page=per_page)
    data = users_schema.dump(users)
    builder.add_message("Listado de usuarios").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    builder = ResponseBuilder()
    user = user_service.get_user(user_id)
    if not user:
        builder.add_message("Usuario no encontrado").add_status_code(404)
        return response_schema.dump(builder.build()), 404

    data = user_schema.dump(user)
    builder.add_message("Usuario encontrado").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200

@user_bp.route('/username/<string:username>', methods=['GET'])
def get_by_username(username):
    builder = ResponseBuilder()
    user = user_service.get_by_username(username)
    if not user:
        builder.add_message("Usuario no encontrado").add_status_code(404)
        return response_schema.dump(builder.build()), 404

    data = user_schema.dump(user)
    builder.add_message("Usuario encontrado").add_status_code(200).add_data(data)
    return response_schema.dump(builder.build()), 200

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    builder = ResponseBuilder()
    try:
        updates = user_schema.load(request.json or {}, partial=True)
    except ValidationError as err:
        builder.add_message("Error de validación").add_status_code(422).add_data(err.messages)
        return response_schema.dump(builder.build()), 422

    # Preparar kwargs para el servicio
    data = {}
    if getattr(updates, 'username', None):
        data['username'] = updates.username
    if getattr(updates, 'email', None):
        data['email'] = updates.email
    if getattr(updates, 'password_hash', None):
        data['password'] = updates.password_hash

    updated = user_service.update_user(user_id, **data)
    if updated is None:
        builder.add_message("Usuario no encontrado o sin cambios").add_status_code(404)
        return response_schema.dump(builder.build()), 404

    result = user_schema.dump(updated)
    builder.add_message("Usuario actualizado").add_status_code(200).add_data(result)
    return response_schema.dump(builder.build()), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    builder = ResponseBuilder()
    success = user_service.delete_user(user_id)
    if not success:
        builder.add_message("Usuario no encontrado").add_status_code(404)
        return response_schema.dump(builder.build()), 404

    builder.add_message("Usuario eliminado").add_status_code(204)
    # 204 No Content típicamente no retorna body, pero Marshmallow lo incluirá vacío.
    return response_schema.dump(builder.build()), 204
