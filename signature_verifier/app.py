import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from utils.preprocessing import preprocess_signature
from utils.siamese import verify_signatures, load_siamese_model

app = Flask(__name__)
app.secret_key = "super_secret_key_for_flash"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

# Load Siamese Model globally on startup
MODEL_PATH = "utils/siamese_signature_model.h5"  # Pre-trained Siamese model weights
siamese_model = load_siamese_model(MODEL_PATH)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    signature_path = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        file = request.files.get('signature')
        
        if file and file.filename != '':
            filename = secure_filename(f"{email}_sig.png")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Save user to DB
            new_user = User(name=name, email=email, signature_path=filepath)
            db.session.add(new_user)
            db.session.commit()
            flash('User registered successfully with signature!', 'success')
            return redirect(url_for('index'))
            
    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        file = request.files.get('signature')
        
        user = User.query.get(user_id)
        if not user:
            flash('Selected user not found.', 'danger')
            return redirect(url_for('verify'))
            
        if file and file.filename != '':
            test_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_temp.png')
            file.save(test_path)
            
            # Perform Siamese Verification
            is_genuine, similarity_score = verify_signatures(
                siamese_model, user.signature_path, test_path
            )
            
            return render_template('verify_result.html', 
                                   user=user, 
                                   is_genuine=is_genuine, 
                                   score=round(similarity_score * 100, 2))
                                   
    users = User.query.all()
    return render_template('verify.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)