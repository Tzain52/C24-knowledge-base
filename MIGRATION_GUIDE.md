# SQLite Migration Guide

## What Changed?

Your Cars24 Product Portal now uses **SQLite database** instead of JSON files for better:
- ✅ Data safety (ACID transactions)
- ✅ Concurrent access (multiple users)
- ✅ Performance (faster queries)
- ✅ Reliability (no data corruption)

## Files Added

1. **models.py** - Database models
2. **app_sqlite.py** - New Flask app with SQLite
3. **migrate_to_sqlite.py** - Migration script
4. **backup_database.py** - Backup utility
5. **projects.db** - SQLite database (created automatically)

## Migration Steps

### Step 1: Install Dependencies

```bash
cd /Users/a38371/Desktop/C24-KnowledgeBase
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Stop Current Server

If your Flask server is running, stop it:
```bash
# Press Ctrl+C in the terminal where it's running
# Or kill the process:
lsof -ti:5000 | xargs kill -9
```

### Step 3: Run Migration

```bash
python3 migrate_to_sqlite.py
```

This will:
- Read your existing `projects_data.json`
- Create SQLite database `projects.db`
- Transfer all projects
- Create backup of JSON file

### Step 4: Replace Old App

```bash
# Backup old app
cp app.py app_old.py

# Replace with SQLite version
cp app_sqlite.py app.py
```

### Step 5: Start New Server

```bash
python app.py
```

Visit: http://localhost:5000

## Verification

Check that all your projects are there:

```bash
python3 -c "from app import app, Project; \
with app.app_context(): \
    print(f'Total projects: {Project.query.count()}')"
```

## Backup Your Data

### Manual Backup
```bash
python3 backup_database.py
```

This creates:
- `backups/projects_YYYYMMDD_HHMMSS.db` (SQLite backup)
- `backups/projects_YYYYMMDD_HHMMSS.json` (JSON export)

### Automatic Daily Backup

Add to crontab:
```bash
crontab -e
```

Add this line:
```
0 2 * * * cd /Users/a38371/Desktop/C24-KnowledgeBase && /usr/bin/python3 backup_database.py
```

## Database Location

Your database is stored at:
```
/Users/a38371/Desktop/C24-KnowledgeBase/projects.db
```

## Rollback (If Needed)

If something goes wrong:

```bash
# Stop server
lsof -ti:5000 | xargs kill -9

# Restore old app
cp app_old.py app.py

# Start server
python app.py
```

Your JSON file is backed up as `projects_data.json.backup`

## Database Management

### View All Projects
```bash
sqlite3 projects.db "SELECT id, name, business_vertical FROM projects;"
```

### Count Projects
```bash
sqlite3 projects.db "SELECT COUNT(*) FROM projects;"
```

### Export to JSON
```bash
python3 backup_database.py
```

### Restore from Backup
```bash
# Restore database file
cp backups/projects_20241217_140000.db projects.db

# Or restore from JSON
python3 -c "
from app import app, db, Project
import json

with app.app_context():
    # Clear existing
    Project.query.delete()
    
    # Load backup
    with open('backups/projects_20241217_140000.json') as f:
        data = json.load(f)
    
    # Import
    for p in data:
        project = Project.from_dict(p)
        db.session.add(project)
    
    db.session.commit()
    print('Restored!')
"
```

## Advantages Over JSON

| Feature | JSON | SQLite |
|---------|------|--------|
| Concurrent writes | ❌ | ✅ |
| Data corruption protection | ❌ | ✅ |
| Transaction support | ❌ | ✅ |
| Complex queries | ❌ | ✅ |
| Performance (1000+ records) | Slow | Fast |
| Automatic timestamps | ❌ | ✅ |
| Data validation | ❌ | ✅ |

## Troubleshooting

### Error: "No module named 'flask_sqlalchemy'"
```bash
pip install flask-sqlalchemy
```

### Error: "Database is locked"
Another process is using the database. Stop all Flask instances:
```bash
lsof -ti:5000 | xargs kill -9
```

### Error: "Table already exists"
Database was already created. This is fine, just continue.

### Lost Data?
Check backups folder:
```bash
ls -lh backups/
```

Restore from most recent backup.

## Support

If you encounter issues:
1. Check `backups/` folder for recent backups
2. Your original JSON is saved as `projects_data.json.backup`
3. You can always rollback to the old app

## Next Steps

1. ✅ Test all functionality (add, edit, delete projects)
2. ✅ Set up automatic backups
3. ✅ Update deployment scripts if needed
4. ✅ Monitor database size: `ls -lh projects.db`

Your data is now safer and more reliable! 🎉
