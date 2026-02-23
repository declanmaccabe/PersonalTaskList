# Personal Task List (Flask + SQLite)

Simple web-based task list using Flask and SQLite for local development. Intended to be easy to move to cloud later (containerize or deploy to Azure App Service).

Features
- Task fields: id, title, description, status (New, In Progress, Onhold, Closed), created_date, planned_start_date, due_date, closed_date
- Add new tasks, filter by status
- Data stored in local SQLite (file: tasks.db)

Quick start (Windows PowerShell)

1. Create and activate a venv

    python -m venv venv; .\venv\Scripts\Activate.ps1

2. Install dependencies

    pip install -r requirements.txt

3. Run the app

    python app.py

4. Open http://127.0.0.1:5000 in your browser

Notes
- To push to GitHub, init a repo, add files, commit, and add remote. I didn't add a remote here automatically.
