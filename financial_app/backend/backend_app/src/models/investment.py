from src.models.user import db
from datetime import datetime, timezone

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc))
    current_value = db.Column(db.Float, nullable=False)
    investment_type_id = db.Column(db.Integer, db.ForeignKey('investment_type.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamentos
    investment_type = db.relationship('InvestmentType', backref=db.backref('investments', lazy=True))
    user = db.relationship('User', backref=db.backref('investments', lazy=True))

    def __repr__(self):
        return f'<Investment {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'date': self.date.isoformat() if self.date else None,
            'current_value': self.current_value,
            'investment_type_id': self.investment_type_id,
            'user_id': self.user_id,
            'investment_type': self.investment_type.to_dict() if self.investment_type else None,
            'profit_loss': self.current_value - self.amount,
            'profit_loss_percentage': ((self.current_value - self.amount) / self.amount * 100) if self.amount > 0 else 0
        }

