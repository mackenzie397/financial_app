from src.models.user import db
from datetime import datetime, timezone

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc))
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.Column(db.Text, default='')
    
    # Relacionamentos
    category = db.relationship('Category', backref=db.backref('transactions', lazy=True))
    payment_method = db.relationship('PaymentMethod', backref=db.backref('transactions', lazy=True))
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.description}>'

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'date': self.date.isoformat() if self.date else None,
            'transaction_type': self.transaction_type,
            'category_id': self.category_id,
            'payment_method_id': self.payment_method_id,
            'user_id': self.user_id,
            'notes': self.notes,
            'category_name': self.category.name if self.category else None,
            'payment_method_name': self.payment_method.name if self.payment_method else None
        }

