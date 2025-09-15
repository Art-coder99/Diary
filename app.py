from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import db, User, Trip

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret123'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash("Пользователь уже существует")
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Регистрация успешна")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash("Неверные данные")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_trip', methods=['GET','POST'])
@login_required
def add_trip():
    if request.method == 'POST':
        title = request.form['title']
        location = request.form['location']
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        cost = float(request.form['cost'])
        image = request.files['image']
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)
        new_trip = Trip(title=title, location=location, latitude=latitude,
                        longitude=longitude, cost=cost, image_url=image_path,
                        user_id=current_user.id)
        db.session.add(new_trip)
        db.session.commit()
        flash("Путешествие добавлено")
        return redirect(url_for('view_trips'))
    return render_template('add_trip.html')

@app.route('/view_trips')
@login_required
def view_trips():
    trips = Trip.query.all()
    return render_template('view_trips.html', trips=trips)

if __name__ == '__main__':
    app.run(debug=True)
