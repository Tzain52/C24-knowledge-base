from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)  # Unique constraint
    summary = db.Column(db.Text, nullable=False)
    business_vertical = db.Column(db.String(50), nullable=False)
    product_manager = db.Column(db.String(100), nullable=False)
    
    # Store complex data as JSON strings
    stakeholders = db.Column(db.Text)  # JSON: {"business": [{"name": "...", "email": "..."}], ...}
    core_docs = db.Column(db.Text)     # JSON: PRD, BRD, TRD
    design_docs = db.Column(db.Text)   # JSON: Figma, Miro
    analytics_docs = db.Column(db.Text)  # JSON: GA Events, Dashboards
    other_docs = db.Column(db.Text)    # JSON: Other documents
    tags = db.Column(db.Text)          # JSON string
    related_projects = db.Column(db.Text)  # JSON: list of project IDs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert database model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'summary': self.summary,
            'business_vertical': self.business_vertical,
            'product_manager': self.product_manager,
            'stakeholders': json.loads(self.stakeholders) if self.stakeholders else {},
            'core_docs': json.loads(self.core_docs) if self.core_docs else [],
            'design_docs': json.loads(self.design_docs) if self.design_docs else [],
            'analytics_docs': json.loads(self.analytics_docs) if self.analytics_docs else [],
            'other_docs': json.loads(self.other_docs) if self.other_docs else [],
            'tags': json.loads(self.tags) if self.tags else [],
            'related_projects': json.loads(self.related_projects) if self.related_projects else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def from_dict(data):
        """Create Project from dictionary"""
        return Project(
            name=data.get('name'),
            summary=data.get('summary'),
            business_vertical=data.get('business_vertical'),
            product_manager=data.get('product_manager'),
            stakeholders=json.dumps(data.get('stakeholders', {})),
            core_docs=json.dumps(data.get('core_docs', [])),
            design_docs=json.dumps(data.get('design_docs', [])),
            analytics_docs=json.dumps(data.get('analytics_docs', [])),
            other_docs=json.dumps(data.get('other_docs', [])),
            tags=json.dumps(data.get('tags', [])),
            related_projects=json.dumps(data.get('related_projects', []))
        )
    
    def update_from_dict(self, data):
        """Update existing project from dictionary"""
        self.name = data.get('name', self.name)
        self.summary = data.get('summary', self.summary)
        self.business_vertical = data.get('business_vertical', self.business_vertical)
        self.product_manager = data.get('product_manager', self.product_manager)
        self.stakeholders = json.dumps(data.get('stakeholders', {}))
        self.core_docs = json.dumps(data.get('core_docs', []))
        self.design_docs = json.dumps(data.get('design_docs', []))
        self.analytics_docs = json.dumps(data.get('analytics_docs', []))
        self.other_docs = json.dumps(data.get('other_docs', []))
        self.tags = json.dumps(data.get('tags', []))
        self.related_projects = json.dumps(data.get('related_projects', []))
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Project {self.id}: {self.name}>'
