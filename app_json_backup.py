from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'cars24-secret-key-change-in-production-12345'

# File to store projects data
PROJECTS_FILE = 'projects_data.json'

# Load projects from file or use default
def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    return []

# Save projects to file
def save_projects(projects_list):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects_list, f, indent=2)

# Sample project data - you can easily modify this
projects = [
    {
        "id": 1,
        "name": "Vehicle Inspection System",
        "summary": "AI-powered vehicle inspection and quality assessment platform for accurate vehicle evaluation. Streamlines the inspection process with automated defect detection and quality scoring.",
        "category": "Product",
        "status": "In Development",
        "business_vertical": "VAS",
        "product_manager": "Rahul Sharma",
        "stakeholders": {
            "business": ["Vikram Mehta (VP - VAS)", "Anjali Desai (Business Head)"],
            "product": ["Rahul Sharma (PM)", "Priya Singh (APM)"],
            "design": ["Neha Kapoor (Lead Designer)", "Arjun Patel (UI Designer)"],
            "engineering": ["Amit Kumar (Tech Lead)", "Sneha Reddy (Backend)", "Karan Joshi (ML Engineer)"]
        },
        "documents": {
            "prd": "https://docs.google.com/document/d/sample-prd-1",
            "brd": "https://docs.google.com/document/d/sample-brd-1",
            "trd": "https://docs.google.com/document/d/sample-trd-1",
            "figma": "https://figma.com/file/sample-design-1",
            "other": [
                {"name": "API Documentation", "url": "https://docs.google.com/document/d/sample-api-1"},
                {"name": "User Research", "url": "https://docs.google.com/document/d/sample-research-1"}
            ]
        },
        "tags": ["AI/ML", "Computer Vision", "Mobile"]
    },
    {
        "id": 2,
        "name": "Customer Portal Revamp",
        "summary": "Complete redesign of customer-facing portal with improved UX, faster performance, and new features for seamless car buying and selling experience.",
        "category": "Product",
        "status": "Active",
        "business_vertical": "A2I",
        "product_manager": "Priya Gupta",
        "stakeholders": {
            "business": ["Rajesh Kumar (VP - A2I)", "Meera Sharma (Business Head)"],
            "product": ["Priya Gupta (PM)", "Rohan Das (APM)"],
            "design": ["Kavita Nair (Lead Designer)", "Sanjay Verma (UX Researcher)"],
            "engineering": ["Deepak Singh (Tech Lead)", "Pooja Agarwal (Frontend)", "Rahul Jain (Backend)"]
        },
        "documents": {
            "prd": "https://docs.google.com/document/d/sample-prd-2",
            "brd": "https://docs.google.com/document/d/sample-brd-2",
            "trd": "https://docs.google.com/document/d/sample-trd-2",
            "figma": "https://figma.com/file/sample-design-2",
            "other": [
                {"name": "Analytics Dashboard", "url": "https://docs.google.com/document/d/sample-analytics-2"},
                {"name": "A/B Test Results", "url": "https://docs.google.com/document/d/sample-ab-test-2"}
            ]
        },
        "tags": ["Web", "Mobile", "UX"]
    },
    {
        "id": 3,
        "name": "Dynamic Pricing Engine",
        "summary": "Advanced pricing algorithm that determines fair market value for vehicles based on market trends, vehicle condition, demand-supply dynamics, and historical data.",
        "category": "Product",
        "status": "Active",
        "business_vertical": "I2P",
        "product_manager": "Amit Kumar",
        "stakeholders": {
            "business": ["Suresh Iyer (VP - I2P)", "Lakshmi Rao (Business Head)"],
            "product": ["Amit Kumar (PM)", "Divya Menon (APM)"],
            "design": ["Ravi Shankar (Data Viz Designer)"],
            "engineering": ["Anil Gupta (Tech Lead)", "Priyanka Shah (Data Scientist)", "Vivek Malhotra (Backend)"]
        },
        "documents": {
            "prd": "https://docs.google.com/document/d/sample-prd-3",
            "brd": "https://docs.google.com/document/d/sample-brd-3",
            "trd": "https://docs.google.com/document/d/sample-trd-3",
            "figma": "https://figma.com/file/sample-design-3",
            "other": [
                {"name": "ML Model Documentation", "url": "https://docs.google.com/document/d/sample-ml-3"},
                {"name": "Pricing Strategy", "url": "https://docs.google.com/document/d/sample-strategy-3"}
            ]
        },
        "tags": ["Data Science", "ML", "Analytics"]
    },
    {
        "id": 4,
        "name": "Logistics Optimization Platform",
        "summary": "Real-time vehicle logistics and transportation management system across multiple cities with route optimization and tracking capabilities.",
        "category": "Product",
        "status": "Active",
        "business_vertical": "I2P",
        "product_manager": "Sneha Patel",
        "stakeholders": {
            "business": ["Manish Agarwal (VP - Operations)", "Nisha Reddy (Business Head)"],
            "product": ["Sneha Patel (PM)", "Gaurav Saxena (APM)"],
            "design": ["Simran Kaur (Lead Designer)", "Tarun Bhatt (UI Designer)"],
            "engineering": ["Rajat Sharma (Tech Lead)", "Ankit Verma (Backend)", "Shalini Gupta (DevOps)"]
        },
        "documents": {
            "prd": "https://docs.google.com/document/d/sample-prd-4",
            "brd": "https://docs.google.com/document/d/sample-brd-4",
            "trd": "https://docs.google.com/document/d/sample-trd-4",
            "figma": "https://figma.com/file/sample-design-4",
            "other": [
                {"name": "Integration Guide", "url": "https://docs.google.com/document/d/sample-integration-4"},
                {"name": "SLA Documentation", "url": "https://docs.google.com/document/d/sample-sla-4"}
            ]
        },
        "tags": ["Operations", "Logistics", "Optimization"]
    },
    {
        "id": 5,
        "name": "Challan Management System",
        "summary": "Automated challan processing and payment tracking system for vehicle compliance. Handles traffic violations, pending challans, and payment workflows.",
        "category": "Product",
        "status": "In Development",
        "business_vertical": "Challan",
        "product_manager": "Vikram Singh",
        "stakeholders": {
            "business": ["Ashok Kumar (VP - Compliance)", "Ritu Malhotra (Business Head)"],
            "product": ["Vikram Singh (PM)", "Aditi Sharma (APM)"],
            "design": ["Mohit Jain (Lead Designer)"],
            "engineering": ["Sunil Reddy (Tech Lead)", "Kavita Iyer (Backend)", "Nikhil Gupta (Integration)"]
        },
        "documents": {
            "prd": "https://docs.google.com/document/d/sample-prd-5",
            "brd": "https://docs.google.com/document/d/sample-brd-5",
            "trd": "https://docs.google.com/document/d/sample-trd-5",
            "figma": "https://figma.com/file/sample-design-5",
            "other": [
                {"name": "Compliance Guidelines", "url": "https://docs.google.com/document/d/sample-compliance-5"},
                {"name": "Payment Gateway Integration", "url": "https://docs.google.com/document/d/sample-payment-5"}
            ]
        },
        "tags": ["FinTech", "Compliance", "Payments"]
    },
    {
        "id": 6,
        "name": "VAS Platform",
        "summary": "Comprehensive Value Added Services platform offering insurance, warranty, extended services, and add-ons for vehicle buyers and sellers.",
        "category": "Product",
        "status": "Active",
        "business_vertical": "VAS",
        "product_manager": "Anjali Verma",
        "stakeholders": {
            "business": ["Karthik Rao (VP - VAS)", "Preeti Singh (Business Head)"],
            "product": ["Anjali Verma (PM)", "Rohit Khanna (APM)"],
            "design": ["Shruti Desai (Lead Designer)", "Varun Mehta (UI Designer)"],
            "engineering": ["Manoj Kumar (Tech Lead)", "Swati Agarwal (Frontend)", "Vishal Joshi (Backend)"]
        },
        "documents": {
            "prd": "https://docs.google.com/document/d/sample-prd-6",
            "brd": "https://docs.google.com/document/d/sample-brd-6",
            "trd": "https://docs.google.com/document/d/sample-trd-6",
            "figma": "https://figma.com/file/sample-design-6",
            "other": [
                {"name": "Partner Integration Docs", "url": "https://docs.google.com/document/d/sample-partner-6"},
                {"name": "Revenue Model", "url": "https://docs.google.com/document/d/sample-revenue-6"}
            ]
        },
        "tags": ["Insurance", "Warranty", "Services"]
    }
]

@app.route('/')
def index():
    """Main landing page route"""
    all_projects = load_projects()
    if not all_projects:
        # Use default sample data if no projects exist
        all_projects = projects
        save_projects(all_projects)
    return render_template('index.html', projects=all_projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Individual project detail page"""
    all_projects = load_projects() or projects
    project = next((p for p in all_projects if p['id'] == project_id), None)
    if project:
        return render_template('project_detail.html', project=project)
    return "Project not found", 404

@app.route('/project/new', methods=['GET', 'POST'])
def new_project():
    """Create a new project"""
    if request.method == 'POST':
        all_projects = load_projects() or projects
        
        # Generate new ID
        new_id = max([p['id'] for p in all_projects], default=0) + 1
        
        # Get basic project info
        new_project = {
            "id": new_id,
            "name": request.form.get('name'),
            "summary": request.form.get('summary'),
            "category": request.form.get('category'),
            "business_vertical": request.form.get('business_vertical'),
            "product_manager": request.form.get('product_manager'),
            "stakeholders": {
                "business": request.form.getlist('business_stakeholders'),
                "product": request.form.getlist('product_stakeholders'),
                "design": request.form.getlist('design_stakeholders'),
                "engineering": request.form.getlist('engineering_stakeholders')
            },
            "documents": {},
            "tags": [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        }
        
        # Get custom documents
        doc_names = request.form.getlist('doc_name')
        doc_urls = request.form.getlist('doc_url')
        
        for name, url in zip(doc_names, doc_urls):
            if name and url:
                # Store with lowercase key for consistency
                key = name.lower().replace(' ', '_')
                new_project['documents'][key] = {
                    'name': name,
                    'url': url
                }
        
        all_projects.append(new_project)
        save_projects(all_projects)
        
        flash(f'Project "{new_project["name"]}" created successfully!', 'success')
        return redirect(url_for('project_detail', project_id=new_id))
    
    return render_template('project_form.html', project=None, action='Create')

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit an existing project"""
    all_projects = load_projects() or projects
    project = next((p for p in all_projects if p['id'] == project_id), None)
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Update basic project info
        project['name'] = request.form.get('name')
        project['summary'] = request.form.get('summary')
        project['category'] = request.form.get('category')
        project['business_vertical'] = request.form.get('business_vertical')
        project['product_manager'] = request.form.get('product_manager')
        
        # Update stakeholders
        project['stakeholders'] = {
            "business": request.form.getlist('business_stakeholders'),
            "product": request.form.getlist('product_stakeholders'),
            "design": request.form.getlist('design_stakeholders'),
            "engineering": request.form.getlist('engineering_stakeholders')
        }
        
        # Update tags
        project['tags'] = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        
        # Update documents
        project['documents'] = {}
        doc_names = request.form.getlist('doc_name')
        doc_urls = request.form.getlist('doc_url')
        
        for name, url in zip(doc_names, doc_urls):
            if name and url:
                key = name.lower().replace(' ', '_')
                project['documents'][key] = {
                    'name': name,
                    'url': url
                }
        
        save_projects(all_projects)
        
        flash(f'Project "{project["name"]}" updated successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('project_form.html', project=project, action='Edit')

@app.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    """Delete a project"""
    all_projects = load_projects() or projects
    project = next((p for p in all_projects if p['id'] == project_id), None)
    
    if project:
        all_projects.remove(project)
        save_projects(all_projects)
        flash(f'Project "{project["name"]}" deleted successfully!', 'success')
    else:
        flash('Project not found', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
