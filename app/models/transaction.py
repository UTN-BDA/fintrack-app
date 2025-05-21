from app.extensions import db

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255))
    method = db.Column(db.String(50))
    is_income = db.Column(db.Boolean, nullable=False, default=False)
    deleted = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    user = db.relationship('User', back_populates='transactions')
    category = db.relationship('Category', back_populates='transactions')