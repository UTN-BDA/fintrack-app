from app.extensions import db

class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    is_recurring = db.Column(db.Boolean, default=False)
    transactions = db.relationship('Transaction', back_populates='category', lazy='dynamic')