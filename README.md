# Cars24 Projects Landing Page

A professional landing page to showcase Cars24 organization projects.

## Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, TailwindCSS
- **Icons**: Lucide Icons

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure
```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   └── index.html     # Landing page
├── static/            # Static files (CSS, JS, images)
│   └── css/
└── README.md          # This file
```

## Updating Projects

Edit the `projects` list in `app.py` to add, remove, or modify projects.
