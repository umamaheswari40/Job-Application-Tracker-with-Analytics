from datetime import datetime
from app import db
from app.models.application import JobApplication
from app.models.status_history import StatusHistory

def create_application(user_id, data):
    """
    Create a new job application and initial status history
    
    Args:
        user_id (int): ID of the user creating the application
        data (dict): Application data
        
    Returns:
        tuple: (success: bool, message: str, application: JobApplication or None)
    """
    try:
        # Validate required fields
        if not data.get('company_name'):
            return False, 'Company name is required.', None
        if not data.get('position'):
            return False, 'Position is required.', None
        if not data.get('applied_date'):
            return False, 'Applied date is required.', None
        
        # Create application
        application = JobApplication(
            user_id=user_id,
            company_name=data.get('company_name'),
            position=data.get('position'),
            location=data.get('location'),
            job_url=data.get('job_url'),
            status=data.get('status', 'applied'),
            salary_range=data.get('salary_range'),
            notes=data.get('notes'),
            applied_date=datetime.strptime(data.get('applied_date'), '%Y-%m-%d').date()
        )
        
        db.session.add(application)
        db.session.flush()  # Get application.id without committing
        
        # Create initial status history
        history = StatusHistory(
            application_id=application.id,
            old_status=None,
            new_status=application.status,
            changed_at=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()
        
        return True, 'Application created successfully!', application
    except Exception as e:
        db.session.rollback()
        return False, f'Failed to create application: {str(e)}', None

def get_user_applications(user_id, filters=None):
    """
    Get all applications for a user
    
    Args:
        user_id (int): User ID
        filters (dict): Optional filters (status, company_name)
        
    Returns:
        list: List of JobApplication objects
    """
    try:
        query = JobApplication.query.filter_by(user_id=user_id)
        
        if filters:
            if filters.get('status'):
                query = query.filter_by(status=filters['status'])
            if filters.get('company_name'):
                query = query.filter(JobApplication.company_name.ilike(f"%{filters['company_name']}%"))
        
        return query.order_by(JobApplication.applied_date.desc()).all()
    except Exception as e:
        return []

def get_application_by_id(application_id, user_id):
    """
    Get a single application by ID (with user verification)
    
    Args:
        application_id (int): Application ID
        user_id (int): User ID for verification
        
    Returns:
        JobApplication or None
    """
    try:
        return JobApplication.query.filter_by(id=application_id, user_id=user_id).first()
    except Exception as e:
        return None

def update_application(application_id, user_id, data):
    """
    Update a job application and track status changes
    
    Args:
        application_id (int): Application ID
        user_id (int): User ID for verification
        data (dict): Updated application data
        
    Returns:
        tuple: (success: bool, message: str, application: JobApplication or None)
    """
    try:
        application = get_application_by_id(application_id, user_id)
        if not application:
            return False, 'Application not found.', None
        
        # Track old status for history
        old_status = application.status
        new_status = data.get('status', application.status)
        
        # Update application fields
        application.company_name = data.get('company_name', application.company_name)
        application.position = data.get('position', application.position)
        application.location = data.get('location', application.location)
        application.job_url = data.get('job_url', application.job_url)
        application.status = new_status
        application.salary_range = data.get('salary_range', application.salary_range)
        application.notes = data.get('notes', application.notes)
        
        if data.get('applied_date'):
            application.applied_date = datetime.strptime(data.get('applied_date'), '%Y-%m-%d').date()
        
        application.updated_at = datetime.utcnow()
        
        # Create status history if status changed
        if old_status != new_status:
            history = StatusHistory(
                application_id=application.id,
                old_status=old_status,
                new_status=new_status,
                changed_at=datetime.utcnow(),
                notes=data.get('status_notes')
            )
            db.session.add(history)
        
        db.session.commit()
        
        return True, 'Application updated successfully!', application
    except Exception as e:
        db.session.rollback()
        return False, f'Failed to update application: {str(e)}', None

def delete_application(application_id, user_id):
    """
    Delete a job application (cascade deletes status history)
    
    Args:
        application_id (int): Application ID
        user_id (int): User ID for verification
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        application = get_application_by_id(application_id, user_id)
        if not application:
            return False, 'Application not found.'
        
        db.session.delete(application)
        db.session.commit()
        
        return True, 'Application deleted successfully!'
    except Exception as e:
        db.session.rollback()
        return False, f'Failed to delete application: {str(e)}'