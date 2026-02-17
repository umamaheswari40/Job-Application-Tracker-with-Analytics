from datetime import datetime
from app import db


class JobApplication(db.Model):
    """Job application model"""
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    job_url = db.Column(db.String(500))
    status = db.Column(db.String(50), nullable=False, default='applied', index=True)
    salary_range = db.Column(db.String(100))
    notes = db.Column(db.Text)
    applied_date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    status_history = db.relationship('StatusHistory', backref='application', lazy='dynamic', 
                                    cascade='all, delete-orphan', order_by='StatusHistory.changed_at.desc()')
    
    def __repr__(self):
        return f'<JobApplication {self.company_name} - {self.position}>'