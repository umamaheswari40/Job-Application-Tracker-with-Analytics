from datetime import datetime
from app import db


class StatusHistory(db.Model):
    """Status history tracking model"""
    __tablename__ = 'status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('job_applications.id'), nullable=False, index=True)
    old_status = db.Column(db.String(50))  # NULL for initial entry
    new_status = db.Column(db.String(50), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<StatusHistory {self.old_status} → {self.new_status}>'