from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Project
import os

app = Flask(__name__)
app.secret_key = 'cars24-secret-key-change-in-production-12345'

# Helper functions for rich document previews
def get_document_embed_info(url):
    """Detect document type and return embed information"""
    if not url:
        return {'type': 'link', 'embed_url': None}
    
    # Google Docs
    if 'docs.google.com/document' in url:
        # Convert to embed URL
        doc_id = url.split('/d/')[1].split('/')[0] if '/d/' in url else None
        if doc_id:
            return {
                'type': 'google_doc',
                'embed_url': f'https://docs.google.com/document/d/{doc_id}/preview',
                'icon': 'google-doc'
            }
    
    # Google Sheets
    elif 'docs.google.com/spreadsheets' in url:
        doc_id = url.split('/d/')[1].split('/')[0] if '/d/' in url else None
        if doc_id:
            return {
                'type': 'google_sheet',
                'embed_url': f'https://docs.google.com/spreadsheets/d/{doc_id}/preview',
                'icon': 'google-sheet'
            }
    
    # Figma
    elif 'figma.com' in url:
        return {
            'type': 'figma',
            'embed_url': f'https://www.figma.com/embed?embed_host=share&url={url}',
            'icon': 'figma'
        }
    
    # Notion
    elif 'notion.so' in url or 'notion.site' in url:
        return {
            'type': 'notion',
            'embed_url': url,
            'icon': 'notion'
        }
    
    # Default - just a link
    return {'type': 'link', 'embed_url': None, 'icon': 'link'}

# Register template filter
@app.template_filter('doc_embed')
def doc_embed_filter(url):
    return get_document_embed_info(url)

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
    # Get all projects for related projects lookup
    all_projects = Project.query.all()
    all_projects_list = [p.to_dict() for p in all_projects]
    return render_template('project_detail.html', project=project.to_dict(), all_projects=all_projects_list)

@app.route('/project/new', methods=['GET', 'POST'])
def new_project():
    """Create a new project"""
    if request.method == 'POST':
        project_name = request.form.get('name')
        
        # Check for duplicate name
        existing = Project.query.filter_by(name=project_name).first()
        if existing:
            flash(f'Project with name "{project_name}" already exists!', 'error')
            all_projects = Project.query.order_by(Project.name).all()
            return render_template('project_form.html', project=None, action='Create', all_projects=all_projects)
        
        # Collect project data
        project_data = {
            'name': project_name,
            'summary': request.form.get('summary'),
            'business_vertical': request.form.get('business_vertical'),
            'product_manager': request.form.get('product_manager'),
            'stakeholders': {
                'business': [],
                'product': [],
                'design': [],
                'engineering': []
            },
            'core_docs': [],
            'design_docs': [],
            'analytics_docs': [],
            'other_docs': [],
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        }
        
        # Process stakeholders with emails
        for role in ['business', 'product', 'design', 'engineering']:
            names = request.form.getlist(f'{role}_stakeholder_name')
            emails = request.form.getlist(f'{role}_stakeholder_email')
            for name, email in zip(names, emails):
                if name:
                    project_data['stakeholders'][role].append({
                        'name': name,
                        'email': email if email else ''
                    })
        
        # Process documents by category
        doc_categories = request.form.getlist('doc_category')
        doc_names = request.form.getlist('doc_name')
        doc_urls = request.form.getlist('doc_url')
        
        for category, name, url in zip(doc_categories, doc_names, doc_urls):
            if name and url:
                doc_obj = {'name': name, 'url': url}
                if category == 'core':
                    project_data['core_docs'].append(doc_obj)
                elif category == 'design':
                    project_data['design_docs'].append(doc_obj)
                elif category == 'analytics':
                    project_data['analytics_docs'].append(doc_obj)
                else:
                    project_data['other_docs'].append(doc_obj)
        
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
            all_projects = Project.query.order_by(Project.name).all()
            return render_template('project_form.html', project=None, action='Create', all_projects=all_projects)
    
    # Get all projects for related projects dropdown
    all_projects = Project.query.order_by(Project.name).all()
    return render_template('project_form.html', project=None, action='Create', all_projects=all_projects)

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit an existing project"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project_name = request.form.get('name')
        
        # Check for duplicate name (excluding current project)
        existing = Project.query.filter(Project.name == project_name, Project.id != project_id).first()
        if existing:
            flash(f'Project with name "{project_name}" already exists!', 'error')
            all_projects = Project.query.filter(Project.id != project_id).order_by(Project.name).all()
            return render_template('project_form.html', project=project.to_dict(), action='Edit', all_projects=all_projects)
        
        # Collect updated data
        updated_data = {
            'name': project_name,
            'summary': request.form.get('summary'),
            'business_vertical': request.form.get('business_vertical'),
            'product_manager': request.form.get('product_manager'),
            'stakeholders': {
                'business': [],
                'product': [],
                'design': [],
                'engineering': []
            },
            'core_docs': [],
            'design_docs': [],
            'analytics_docs': [],
            'other_docs': [],
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        }
        
        # Process stakeholders with emails
        for role in ['business', 'product', 'design', 'engineering']:
            names = request.form.getlist(f'{role}_stakeholder_name')
            emails = request.form.getlist(f'{role}_stakeholder_email')
            for name, email in zip(names, emails):
                if name:
                    updated_data['stakeholders'][role].append({
                        'name': name,
                        'email': email if email else ''
                    })
        
        # Process documents by category
        doc_categories = request.form.getlist('doc_category')
        doc_names = request.form.getlist('doc_name')
        doc_urls = request.form.getlist('doc_url')
        
        for category, name, url in zip(doc_categories, doc_names, doc_urls):
            if name and url:
                doc_obj = {'name': name, 'url': url}
                if category == 'core':
                    updated_data['core_docs'].append(doc_obj)
                elif category == 'design':
                    updated_data['design_docs'].append(doc_obj)
                elif category == 'analytics':
                    updated_data['analytics_docs'].append(doc_obj)
                else:
                    updated_data['other_docs'].append(doc_obj)
        
        # Update project
        try:
            project.update_from_dict(updated_data)
            db.session.commit()
            
            flash(f'Project "{project.name}" updated successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'error')
            all_projects = Project.query.filter(Project.id != project_id).order_by(Project.name).all()
            return render_template('project_form.html', project=project.to_dict(), action='Edit', all_projects=all_projects)
    
    # Get all projects for related projects dropdown (excluding current)
    all_projects = Project.query.filter(Project.id != project_id).order_by(Project.name).all()
    return render_template('project_form.html', project=project.to_dict(), action='Edit', all_projects=all_projects)

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

@app.route('/api/search')
def search_projects():
    """API endpoint for searching projects"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return {'projects': []}
    
    # Search in name, summary, product_manager, business_vertical, and tags
    projects = Project.query.all()
    results = []
    
    for project in projects:
        project_dict = project.to_dict()
        searchable_text = ' '.join([
            project_dict['name'],
            project_dict['summary'],
            project_dict['product_manager'],
            project_dict['business_vertical'],
            ' '.join(project_dict['tags'])
        ]).lower()
        
        if query in searchable_text:
            results.append({
                'id': project_dict['id'],
                'name': project_dict['name'],
                'summary': project_dict['summary'][:100] + '...' if len(project_dict['summary']) > 100 else project_dict['summary'],
                'business_vertical': project_dict['business_vertical'],
                'product_manager': project_dict['product_manager']
            })
    
    return {'projects': results}

@app.route('/api/business-verticals')
def get_business_verticals():
    """API endpoint to get all unique business verticals"""
    projects = Project.query.all()
    verticals = set()
    
    for project in projects:
        if project.business_vertical:
            verticals.add(project.business_vertical)
    
    return {'verticals': sorted(list(verticals))}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
