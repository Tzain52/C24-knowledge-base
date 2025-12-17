#!/usr/bin/env python3
"""
Schema migration script - reads from old schema, writes to new schema
"""
import json
import sqlite3
import os

def migrate_database():
    """Migrate database from old schema to new schema"""
    
    print("=" * 60)
    print("Schema Migration - Database Structure Update")
    print("=" * 60)
    print()
    
    db_file = 'projects.db'
    backup_file = 'projects_old_schema.db'
    
    if not os.path.exists(db_file):
        print("❌ Database file not found!")
        return
    
    # Step 1: Backup old database
    print("💾 Creating backup...")
    import shutil
    shutil.copy(db_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Step 2: Read old data
    print("\n📊 Reading existing projects...")
    conn = sqlite3.connect(backup_file)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM projects")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        projects_data = []
        for row in rows:
            proj = dict(zip(columns, row))
            projects_data.append(proj)
        
        print(f"✅ Found {len(projects_data)} projects")
        conn.close()
    except Exception as e:
        print(f"❌ Error reading old data: {e}")
        conn.close()
        return
    
    # Step 3: Delete old database and create new schema
    print("\n🔧 Creating new database schema...")
    os.remove(db_file)
    
    # Import with new schema
    from app import app, db, Project
    
    with app.app_context():
        db.create_all()
        print("✅ New schema created")
        
        # Step 4: Migrate data
        print("\n📦 Migrating data to new structure...")
        migrated = 0
        errors = 0
        
        for old_proj in projects_data:
            try:
                # Parse JSON fields
                stakeholders = json.loads(old_proj.get('stakeholders', '{}'))
                documents = json.loads(old_proj.get('documents', '{}'))
                tags = json.loads(old_proj.get('tags', '[]'))
                
                # Convert documents to categorized structure
                core_docs = []
                design_docs = []
                analytics_docs = []
                other_docs = []
                
                for key, doc in documents.items():
                    doc_name = doc.get('name', key) if isinstance(doc, dict) else key
                    doc_url = doc.get('url', doc) if isinstance(doc, dict) else doc
                    
                    doc_lower = doc_name.lower()
                    doc_obj = {'name': doc_name, 'url': doc_url}
                    
                    if any(term in doc_lower for term in ['prd', 'brd', 'trd', 'spec', 'requirement']):
                        core_docs.append(doc_obj)
                    elif any(term in doc_lower for term in ['figma', 'miro', 'design', 'wireframe', 'mockup']):
                        design_docs.append(doc_obj)
                    elif any(term in doc_lower for term in ['analytics', 'ga', 'event', 'dashboard', 'metric']):
                        analytics_docs.append(doc_obj)
                    else:
                        other_docs.append(doc_obj)
                
                # Convert stakeholders to new format with emails
                new_stakeholders = {
                    'business': [],
                    'product': [],
                    'design': [],
                    'engineering': []
                }
                
                for role in ['business', 'product', 'design', 'engineering']:
                    old_list = stakeholders.get(role, [])
                    for person in old_list:
                        if isinstance(person, dict):
                            new_stakeholders[role].append(person)
                        else:
                            new_stakeholders[role].append({
                                'name': person,
                                'email': ''
                            })
                
                # Create new project
                new_proj_data = {
                    'name': old_proj['name'],
                    'summary': old_proj['summary'],
                    'business_vertical': old_proj['business_vertical'],
                    'product_manager': old_proj['product_manager'],
                    'stakeholders': new_stakeholders,
                    'core_docs': core_docs,
                    'design_docs': design_docs,
                    'analytics_docs': analytics_docs,
                    'other_docs': other_docs,
                    'tags': tags,
                    'related_projects': []
                }
                
                new_project = Project.from_dict(new_proj_data)
                db.session.add(new_project)
                migrated += 1
                print(f"  ✓ Migrated: {old_proj['name']}")
                
            except Exception as e:
                errors += 1
                print(f"  ✗ Error migrating '{old_proj.get('name', 'Unknown')}': {e}")
        
        # Commit changes
        try:
            db.session.commit()
            print(f"\n🎉 Migration complete!")
            print(f"   ✅ Successfully migrated: {migrated} projects")
            if errors > 0:
                print(f"   ❌ Errors: {errors} projects")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing: {e}")
            return
        
        # Verify
        print("\n🔍 Verifying migration...")
        final_count = Project.query.count()
        print(f"✅ Database now has {final_count} projects")
        
        if final_count > 0:
            sample = Project.query.first()
            sample_dict = sample.to_dict()
            print(f"\n📋 Sample project: {sample_dict['name']}")
            print(f"   📄 Core Docs: {len(sample_dict['core_docs'])}")
            print(f"   🎨 Design Docs: {len(sample_dict['design_docs'])}")
            print(f"   📊 Analytics Docs: {len(sample_dict['analytics_docs'])}")
            print(f"   📝 Other Docs: {len(sample_dict['other_docs'])}")

if __name__ == '__main__':
    print()
    migrate_database()
    print()
    print("=" * 60)
    print("✅ Migration complete!")
    print("📁 Old database backed up as: projects_old_schema.db")
    print("🚀 You can now restart your server")
    print("=" * 60)
    print()
