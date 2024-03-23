from flask import Flask, send_from_directory, session, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import uuid
import json
import os


app = Flask(__name__, static_folder='templates/assets', static_url_path='/templates/assets')
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unichoice.db'
app.config['STATIC_FOLDER'] = 'assets'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(1000), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    regno = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    session_id = db.Column(db.String(100), nullable=True)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    option = db.Column(db.String(100), nullable=False)
    user = db.relationship('User', backref=db.backref('votes', lazy=True))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        regno = request.form['regno']
        phone = request.form['phone']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('signup'))
        user = User(email=email, password=hashed_password, name=name, regno=regno, phone=phone)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            user.session_id = str(uuid.uuid4())
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/profile', methods=['GET'])
@login_required
def dashboard():
    if not current_user.session_id:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/logout')
@login_required
def logout():
    current_user.session_id = None
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.', 'danger')
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/user', methods=['GET'])
@login_required
def user():
    name=current_user.name
    email=current_user.email
    regno=current_user.regno
    phone=current_user.phone
    user_id=current_user.id
    profilepic = 'assets/profilepics/'+str(current_user.id)+'.jpg'
    if not os.path.exists(profilepic):
        res=json.dumps({'name':name,'email':email,'regno':regno,'phone':phone,'user_id':user_id,'profilepic':profilepic})
    else:
        res=json.dumps({'name':name,'email':email,'regno':regno,'phone':phone,'user_id':user_id})
    return res

@app.route('/update', methods=['POST'])
@login_required
def update():
    name = request.form['name']
    regno = request.form['regno']
    phone = request.form['phone']
    current_user.name=name
    current_user.regno=regno
    current_user.phone=phone
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/updateprofilepic', methods=['POST'])
@login_required
def updateprofilepic():
    profilepic = request.files['profilepic']
    profilepic.save('templates/assets/profilepics/'+str(current_user.id)+'.jpg')
    return render_template('profile.html')

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    profilepic = 'templates/assets/profilepics/'+str(current_user.id)+'.jpg'
    if os.path.exists(profilepic):
        os.remove(profilepic)
        db.session.delete(current_user)
        db.session.commit()
    flash('Account deleted successfully.', 'danger')
    return redirect(url_for('signup'))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/contactus', methods=['GET'])
def contactus():
    return render_template('contactus.html')

@app.route('/submitcontactform', methods=['POST'])
def submitcontactform():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    contact = Contact(name=name, email=email, message=message)
    db.session.add(contact)
    db.session.commit()
    flash('Message sent successfully.', 'success')
    return redirect(url_for('contactus'))

@app.route('/vote', methods=['POST'])
@login_required
def vote():
    option = request.form['option']
    if Vote.query.filter_by(user_id=current_user.id).first():
        flash('You have already voted.', 'danger')
        return redirect(url_for('voting'))
    vote = Vote(user_id=current_user.id, option=option)
    db.session.add(vote)
    db.session.commit()
    flash('Vote submitted successfully.', 'success')
    return redirect(url_for('voting'))

@app.route('/voting', methods=['GET'])
def voting():
    return render_template('voting.html')

@app.route('/termsandconditions', methods=['GET'])
def termsandconditions():
    return render_template('termsandconditions.html')

@app.route('/privacypolicy', methods=['GET'])
def privacypolicy():
    return render_template('privacypolicy.html')

@app.route('/assets/<path:path>', methods=['GET'])
def send_assets(path):
    return send_from_directory('templates/assets', path)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
