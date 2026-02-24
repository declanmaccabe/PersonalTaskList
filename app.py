from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_AZURE_APP_SERVICE = bool(os.getenv('WEBSITE_SITE_NAME'))
DB_PATH = '/home/tasks.db' if IS_AZURE_APP_SERVICE else os.path.join(BASE_DIR, 'tasks.db')
DEFAULT_DB_URI = f'sqlite:///{DB_PATH}'


def build_sqlalchemy_uri():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return DEFAULT_DB_URI

    # full SQLAlchemy/database URI
    if '://' in database_url:
        return database_url

    # Azure ODBC-style connection string
    return f"mssql+pyodbc:///?odbc_connect={quote_plus(database_url)}"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = build_sqlalchemy_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='New')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    planned_start_date = db.Column(db.Date, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    closed_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Task {self.id} {self.title}>'


# create database tables on startup (prototype behavior)
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def index():
    status_filter = request.args.get('status', 'All')
    search = request.args.get('search', '')

    counts = {
        'New': Task.query.filter_by(status='New').count(),
        'In Progress': Task.query.filter_by(status='In Progress').count(),
        'Onhold': Task.query.filter_by(status='Onhold').count(),
        'Closed': Task.query.filter_by(status='Closed').count(),
    }

    q = Task.query
    if status_filter and status_filter != 'All':
        q = q.filter_by(status=status_filter)
    if search:
        q = q.filter(Task.title.ilike(f'%{search}%'))

    tasks = q.order_by(Task.created_date.desc()).all()
    statuses = ['All', 'New', 'In Progress', 'Onhold', 'Closed']
    return render_template(
        'index.html',
        tasks=tasks,
        statuses=statuses,
        selected_status=status_filter,
        search=search,
        counts=counts
    )


@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status') or 'New'
    planned_start = request.form.get('planned_start_date') or None
    due_date = request.form.get('due_date') or None

    planned = datetime.strptime(planned_start, '%Y-%m-%d').date() if planned_start else None
    due = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None

    t = Task(title=title, description=description, status=status, planned_start_date=planned, due_date=due)
    if status == 'Closed':
        t.closed_date = datetime.utcnow()

    db.session.add(t)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/close/<int:task_id>', methods=['POST'])
def close_task(task_id):
    t = Task.query.get_or_404(task_id)
    t.status = 'Closed'
    t.closed_date = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    t = Task.query.get_or_404(task_id)
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status') or t.status
    planned_start = request.form.get('planned_start_date') or None
    due_date = request.form.get('due_date') or None

    t.title = title
    t.description = description
    # parse dates
    t.planned_start_date = datetime.strptime(planned_start, '%Y-%m-%d').date() if planned_start else None
    t.due_date = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None

    # handle status transitions and closed_date
    prev_status = t.status
    t.status = status
    if status == 'Closed' and not t.closed_date:
        t.closed_date = datetime.utcnow()
    if prev_status == 'Closed' and status != 'Closed':
        t.closed_date = None

    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    is_debug = os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=is_debug)
