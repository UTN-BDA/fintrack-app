from marshmallow import Schema, fields, post_load
from app.models import Transaction

class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Decimal(as_string=True, required=True)
    date = fields.Date(required=True)
    description = fields.Str()
    method = fields.Str()
    is_income = fields.Bool(required=True)
    deleted = fields.Bool()

    user_id = fields.Int(required=True)
    category_id = fields.Int(allow_none=True)

    # Relaciones
    user = fields.Nested('UserSchema', only=('id', 'username'), dump_only=True)
    category = fields.Nested('CategorySchema', only=('id', 'name'), dump_only=True)

    @post_load
    def make_transaction(self, data, **kwargs):
        return Transaction(**data)
