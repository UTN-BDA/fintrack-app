from app.models import User
from marshmallow import fields, Schema, post_load

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password_hash = fields.Str(load_only=True, required=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)