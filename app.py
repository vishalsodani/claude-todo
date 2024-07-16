from flask import Flask, render_template, request, redirect, url_for, g, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

DATABASE = 'todos.db'
USERNAME = os.getenv('TODO_USERNAME')
PASSWORD = os.getenv('TODO_PASSWORD')
print(f"Username: {USERNAME}")
print(f"Password: {PASSWORD}")

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(password)
        if username == USERNAME and password == PASSWORD:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    db = get_db()
    if request.method == 'POST':
        if 'add' in request.form:
            task = request.form['task']
            due_date = request.form['due_date'] or None
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.execute('INSERT INTO todos (task, completed, date_added, due_date) VALUES (?, ?, ?, ?)', 
                       (task, 0, now, due_date))
        elif 'complete' in request.form:
            id = request.form['complete']
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.execute('UPDATE todos SET completed = 1, date_completed = ? WHERE id = ?', (now, id))
        elif 'delete' in request.form:
            id = request.form['delete']
            db.execute('DELETE FROM todos WHERE id = ?', (id,))
        elif 'search' in request.form:
            search = request.form['search']
            todos = db.execute('SELECT * FROM todos WHERE task LIKE ? ORDER BY date_added DESC', (f'%{search}%',)).fetchall()
            db.commit()
            return render_template('index.html', todos=todos, search=search)
        db.commit()
        return redirect(url_for('index'))
    
    todos = db.execute('SELECT * FROM todos ORDER BY date_added DESC').fetchall()
    return render_template('index.html', todos=todos, now=datetime.now().date())

if __name__ == '__main__':
    init_db()
    app.run(debug=True)