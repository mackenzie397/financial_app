from src.models.user import db
from datetime import datetime, timezone

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    target_date = db.Column(db.Date)
    created_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'paused'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamento
    user = db.relationship('User', backref=db.backref('goals', lazy=True))

    def __repr__(self):
        return f'<Goal {self.name}>'

    def to_dict(self):
        progress_percentage = (self.current_amount / self.target_amount * 100) if self.target_amount > 0 else 0
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'status': self.status,
            'user_id': self.user_id,
            'progress_percentage': progress_percentage,
            'remaining_amount': self.target_amount - self.current_amount
        }

