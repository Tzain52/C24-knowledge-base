from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Project
import os

app = Flask(__name__)
app.secret_key = 'cars24-secret-key-change-in-production-12345'

# SQLite Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "projects.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

@app.route('/')
def index():
    """Main landing page route"""
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    projects_list = [p.to_dict() for p in projects]
    return render_template('index.html', projects=projects_list)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Individual project detail page"""
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project.to_dict())

@app.route('/project/new', methods=['GET', 'POST'])
def new_project():
    """Create a new project"""
    if request.method == 'POST':
        # Collect project data
        project_data = {
            'name': request.form.get('name'),
            'summary': request.form.get('summary'),
            'category': request.form.get('category'),
            'business_vertical': request.form.get('business_vertical'),
            'product_manager': request.form.get('product_manager'),
            'stakeholders': {
                'business': [s for s in request.form.getlist('business_stakeholders') if s],
                'product': [s for s in request.form.getlist('product_stakeholders') if s],
                'design': [s for s in request.form.getlist('design_stakeholders') if s],
                'engineering': [s for s in request.form.getlist('engineering_stakeholders') if s]
            },
            'documents': {},
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        }
        
        # Process documents
        doc_names = request.form.getlist('doc_name')
        doc_urls = request.form.getlist('doc_url')
        
        for name, url in zip(doc_names, doc_urls):
            if name and url:
                key = name.lower().replace(' ', '_')
                project_data['documents'][key] = {
                    'name': name,
                    'url': url
                }
        
        # Create and save project
        try:
            project = Project.from_dict(project_data)
            db.session.add(project)
            db.session.commit()
            
            flash(f'Project "{project.name}" created successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating project: {str(e)}', 'error')
            return redirect(url_for('new_project'))
    
    return render_template('project_form.html', project=None, action='Create')

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit an existing project"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        # Collect updated data
        updated_data = {
            'name': request.form.get('name'),
            'summary': request.form.get('summary'),
            'category': request.form.get('category'),
            'business_vertical': request.form.get('business_vertical'),
            'product_manager': request.form.get('product_manager'),
            'stakeholders': {
                'business': [s for s in request.form.getlist('business_stakeholders') if s],
                'product': [s for s in request.form.getlist('product_stakeholders') if s],
                'design': [s for s in request.form.getlist('design_stakeholders') if s],
                'engineering': [s for s in request.form.getlist('engineering_stakeholders') if s]
            },
            'documents': {},
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        }
        
        # Process documents
        doc_names = request.form.getlist('doc_name')
        doc_urls = request.form.getlist('doc_url')
        
        for name, url in zip(doc_names, doc_urls):
            if name and url:
                key = name.lower().replace(' ', '_')
                updated_data['documents'][key] = {
                    'name': name,
                    'url': url
                }
        
        # Update project
        try:
            project.update_from_dict(updated_data)
            db.session.commit()
            
            flash(f'Project "{project.name}" updated successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'error')
            return redirect(url_for('edit_project', project_id=project_id))
    
    return render_template('project_form.html', project=project.to_dict(), action='Edit')

@app.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    """Delete a project"""
    project = Project.query.get_or_404(project_id)
    
    try:
        name = project.name
        db.session.delete(project)
        db.session.commit()
        
        flash(f'Project "{name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting project: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
