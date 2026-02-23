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

## Cloud deployment (Azure App Service + M365/Entra ID)

This is the quickest way to access the app from iPad/laptop anywhere.

### 1) Prepare code for cloud (already done in this project)

- App now reads config from environment variables:
    - `SECRET_KEY`
    - `DATABASE_URL` (optional; defaults to local SQLite)
    - `PORT`
    - `FLASK_DEBUG`
- Production server dependency added: `gunicorn`

### 2) Push repo to GitHub

Use your existing repo or create one and push this project.

### 3) Create Azure App Service

1. Azure Portal -> Create Resource -> Web App
2. Runtime: Python 3.11 (Linux)
3. Publish: Code
4. Connect Deployment Center to your GitHub repo/branch

### 4) Set startup command and app settings

In App Service -> Configuration:

- Startup Command:

    `gunicorn --bind 0.0.0.0:$PORT app:app`

- Application settings:
    - `SECRET_KEY` = strong random value
    - `FLASK_DEBUG` = `0`
    - (optional for now) `DATABASE_URL` = your managed DB connection string

### 5) Enable sign-in with your M365/AD account

In App Service -> Authentication:

1. Add identity provider: Microsoft
2. Select your Microsoft Entra tenant
3. Require authentication for all requests

This gives you AD-backed login without writing auth code first.

### 6) Database recommendation

- For testing: SQLite can work for one instance, but it is not ideal for production scale/reliability.
- For real use: move to Azure SQL or Azure Database for PostgreSQL and set `DATABASE_URL`.

## Fastest rollout estimate

- Basic cloud launch (current app + Entra auth + App Service): ~1 to 3 hours
- Better production setup (managed DB + monitoring + backups): ~1 to 2 days
