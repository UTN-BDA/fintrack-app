from marshmallow import Schema, fields, post_load
from app.models import Category

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    is_favorite = fields.Bool()
    is_recurring = fields.Bool()

    @post_load
    def make_category(self, data, **kwargs):
        return Category(**data)
