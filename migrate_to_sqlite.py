#!/usr/bin/env python3
"""
Migration script to transfer data from JSON to SQLite database
"""
import json
import os
from app_sqlite import app, db, Project

def migrate_json_to_sqlite():
    """Migrate projects from JSON file to SQLite database"""
    
    json_file = 'projects_data.json'
    
    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"❌ JSON file '{json_file}' not found!")
        print("ℹ️  No existing data to migrate. Starting with empty database.")
        return
    
    # Load JSON data
    try:
        with open(json_file, 'r') as f:
            projects_data = json.load(f)
        print(f"✅ Loaded {len(projects_data)} projects from JSON file")
    except json.JSONDecodeError as e:
        print(f"❌ Error reading JSON file: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return
    
    # Migrate to SQLite
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing)
        existing_count = Project.query.count()
        if existing_count > 0:
            print(f"⚠️  Database already has {existing_count} projects")
            response = input("Do you want to clear existing data? (yes/no): ")
            if response.lower() == 'yes':
                Project.query.delete()
                db.session.commit()
                print("✅ Cleared existing data")
        
        # Insert projects
        migrated = 0
        errors = 0
        
        for proj_data in projects_data:
            try:
                # Create project from dictionary
                project = Project.from_dict(proj_data)
                db.session.add(project)
                migrated += 1
                print(f"  ✓ Migrated: {proj_data.get('name', 'Unknown')}")
            except Exception as e:
                errors += 1
                print(f"  ✗ Error migrating '{proj_data.get('name', 'Unknown')}': {e}")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n🎉 Migration complete!")
            print(f"   ✅ Successfully migrated: {migrated} projects")
            if errors > 0:
                print(f"   ❌ Errors: {errors} projects")
            
            # Backup JSON file
            backup_file = 'projects_data.json.backup'
            if not os.path.exists(backup_file):
                import shutil
                shutil.copy(json_file, backup_file)
                print(f"\n💾 Backup created: {backup_file}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing to database: {e}")
            return

if __name__ == '__main__':
    print("=" * 60)
    print("Cars24 Product Portal - JSON to SQLite Migration")
    print("=" * 60)
    print()
    
    migrate_json_to_sqlite()
    
    print()
    print("=" * 60)
    print("Next steps:")
    print("1. Verify data: python3 -c 'from app_sqlite import app, Project; ")
    print("   with app.app_context(): print(f\"Total projects: {Project.query.count()}\")'")
    print("2. Replace app.py with app_sqlite.py")
    print("3. Restart your server")
    print("=" * 60)
