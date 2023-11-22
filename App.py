from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    todos = db.relationship('ToDo', backref='user', lazy=True)


class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    issued_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('todo'))
        else:
            error = "Invalid credentials!"
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/todo')
def todo():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        todos = user.todos
        return render_template('todo.html', user=user, todos=todos)
    else:
        return redirect(url_for('login'))


# ...

@app.route('/add_task', methods=['POST'])
def add_task():
    user_id = session.get('user_id')
    if user_id:
        task = request.form['task']
        priority = request.form['priority']
        new_task = ToDo(user_id=user_id, task=task, priority=priority)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('todo'))
    else:
        return redirect(url_for('login'))

# ...



@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    user_id = session.get('user_id')
    if user_id:
        task = ToDo.query.filter_by(user_id=user_id, id=task_id).first()
        if task:
            db.session.delete(task)
            db.session.commit()
    return redirect(url_for('todo'))

@app.route('/mark_as_done/<int:task_id>', methods=['POST'])
def mark_as_done(task_id):
    user_id = session.get('user_id')
    if user_id:
        task = ToDo.query.filter_by(user_id=user_id, id=task_id).first()
        if task:
            task.done = True
            db.session.commit()
    return redirect(url_for('todo'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
