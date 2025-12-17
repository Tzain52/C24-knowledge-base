#!/usr/bin/env python3
"""
Backup script for SQLite database
Creates timestamped backups and exports to JSON
"""
import os
import shutil
import json
from datetime import datetime
from app_sqlite import app, Project

def backup_database():
    """Create backup of SQLite database"""
    
    # Create backups directory
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Backup SQLite file
    db_file = 'projects.db'
    if os.path.exists(db_file):
        backup_db = os.path.join(backup_dir, f'projects_{timestamp}.db')
        shutil.copy(db_file, backup_db)
        print(f"✅ Database backed up to: {backup_db}")
        db_size = os.path.getsize(backup_db) / 1024  # KB
        print(f"   Size: {db_size:.2f} KB")
    else:
        print("⚠️  No database file found to backup")
    
    # 2. Export to JSON (for portability)
    with app.app_context():
        projects = Project.query.all()
        projects_data = [p.to_dict() for p in projects]
        
        json_backup = os.path.join(backup_dir, f'projects_{timestamp}.json')
        with open(json_backup, 'w') as f:
            json.dump(projects_data, f, indent=2)
        
        print(f"✅ JSON export created: {json_backup}")
        print(f"   Projects: {len(projects_data)}")
    
    # 3. Clean old backups (keep last 30)
    all_backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('projects_')])
    if len(all_backups) > 30:
        for old_backup in all_backups[:-30]:
            os.remove(os.path.join(backup_dir, old_backup))
        print(f"🗑️  Cleaned {len(all_backups) - 30} old backups")
    
    print(f"\n💾 Backup complete! Total backups: {min(len(all_backups), 30)}")

if __name__ == '__main__':
    print("=" * 60)
    print("Cars24 Product Portal - Database Backup")
    print("=" * 60)
    print()
    
    backup_database()
    
    print()
    print("=" * 60)
