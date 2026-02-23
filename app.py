from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'tasks.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
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


# create database tables (convenience for local development)
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def index():
    status_filter = request.args.get('status', 'All')
    search = request.args.get('search', '')

    q = Task.query
    if status_filter and status_filter != 'All':
        q = q.filter_by(status=status_filter)
    if search:
        q = q.filter(Task.title.ilike(f'%{search}%'))

    tasks = q.order_by(Task.created_date.desc()).all()
    statuses = ['All', 'New', 'In Progress', 'Onhold', 'Closed']
    return render_template('index.html', tasks=tasks, statuses=statuses, selected_status=status_filter, search=search)


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


if __name__ == '__main__':
    app.run(debug=True)
