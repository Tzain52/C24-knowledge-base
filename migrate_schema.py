#!/usr/bin/env python3
"""
Schema migration script to update database structure
- Remove category field
- Split documents into core_docs, design_docs, analytics_docs, other_docs
- Add related_projects field
- Update stakeholders to include emails
"""
import json
import os
from app import app, db, Project

def migrate_schema():
    """Migrate database schema and data"""
    
    print("=" * 60)
    print("Schema Migration - Updating Database Structure")
    print("=" * 60)
    print()
    
    with app.app_context():
        # Step 1: Get all existing projects
        print("📊 Reading existing projects...")
        try:
            projects = Project.query.all()
            projects_data = []
            
            for proj in projects:
                proj_dict = proj.to_dict()
                projects_data.append(proj_dict)
            
            print(f"✅ Found {len(projects_data)} projects")
        except Exception as e:
            print(f"❌ Error reading projects: {e}")
            return
        
        # Step 2: Drop and recreate tables
        print("\n🔧 Updating database schema...")
        try:
            db.drop_all()
            db.create_all()
            print("✅ Schema updated successfully")
        except Exception as e:
            print(f"❌ Error updating schema: {e}")
            return
        
        # Step 3: Migrate data to new structure
        print("\n📦 Migrating data to new structure...")
        migrated = 0
        errors = 0
        
        for old_proj in projects_data:
            try:
                # Convert old documents structure to new categorized structure
                core_docs = []
                design_docs = []
                analytics_docs = []
                other_docs = []
                
                # Get old documents (could be dict or list)
                old_docs = old_proj.get('documents', {})
                if isinstance(old_docs, dict):
                    for key, doc in old_docs.items():
                        doc_name = doc.get('name', key) if isinstance(doc, dict) else key
                        doc_url = doc.get('url', doc) if isinstance(doc, dict) else doc
                        
                        # Categorize based on name
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
                
                # Convert old stakeholders (strings) to new format (with emails)
                stakeholders = old_proj.get('stakeholders', {})
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
                            # Already in new format
                            new_stakeholders[role].append(person)
                        else:
                            # Convert string to new format
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
                    'tags': old_proj.get('tags', []),
                    'related_projects': old_proj.get('related_projects', [])
                }
                
                new_project = Project.from_dict(new_proj_data)
                db.session.add(new_project)
                migrated += 1
                print(f"  ✓ Migrated: {old_proj['name']}")
                
            except Exception as e:
                errors += 1
                print(f"  ✗ Error migrating '{old_proj.get('name', 'Unknown')}': {e}")
        
        # Step 4: Commit changes
        try:
            db.session.commit()
            print(f"\n🎉 Migration complete!")
            print(f"   ✅ Successfully migrated: {migrated} projects")
            if errors > 0:
                print(f"   ❌ Errors: {errors} projects")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing to database: {e}")
            return
        
        # Step 5: Verify migration
        print("\n🔍 Verifying migration...")
        try:
            final_count = Project.query.count()
            print(f"✅ Database now has {final_count} projects")
            
            # Show sample of migrated data
            sample = Project.query.first()
            if sample:
                sample_dict = sample.to_dict()
                print(f"\n📋 Sample project structure:")
                print(f"   Name: {sample_dict['name']}")
                print(f"   Core Docs: {len(sample_dict['core_docs'])}")
                print(f"   Design Docs: {len(sample_dict['design_docs'])}")
                print(f"   Analytics Docs: {len(sample_dict['analytics_docs'])}")
                print(f"   Other Docs: {len(sample_dict['other_docs'])}")
                print(f"   Related Projects: {len(sample_dict['related_projects'])}")
        except Exception as e:
            print(f"⚠️  Error verifying: {e}")

if __name__ == '__main__':
    print()
    migrate_schema()
    print()
    print("=" * 60)
    print("Next steps:")
    print("1. Restart your Flask server")
    print("2. Test creating/editing projects")
    print("3. Verify document categories display correctly")
    print("=" * 60)
    print()
