from datetime import datetime
from models.base import db
from config.constants import Visibility


class Attachment(db.Model):
    """Attachment model for storing file paths."""
    __tablename__ = 'attachments'
    
    attachment_id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    attachment_type = db.Column(db.Enum('attachment', 'gallery_image'), nullable=False)
    visibility = db.Column(db.Enum(Visibility.SHOW, Visibility.HIDE), default=Visibility.SHOW)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attachment {self.attachment_id}: {self.file_path}>'