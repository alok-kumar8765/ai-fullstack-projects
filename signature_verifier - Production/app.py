import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from utils.siamese import verify_signatures, load_siamese_model

app = Flask(__name__)
app.secret_key = "super_secret_production_key_change_me"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_multisample.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

# Load AI Model Globally on Server Startup with GPU checks
MODEL_PATH = "utils/siamese_signature_model.h5"
siamese_model = load_siamese_model(MODEL_PATH)

# --- Database Models (One-to-Many Multi-Sample Architecture) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    signatures = db.relationship('SignatureSample', backref='user', lazy=True, cascade='all, delete-orphan')

class SignatureSample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# ==========================================
# WEB UI ROUTES
# ==========================================
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        files = request.files.getlist('signatures') # Multi-sample file inputs
        
        if not files or all(f.filename == '' for f in files):
            flash('Please upload at least one signature reference sample.', 'danger')
            return redirect(request.url)
            
        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'danger')
            return redirect(request.url)

        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.flush() # Secure id generation before committing relations
        
        saved_count = 0
        for idx, file in enumerate(files):
            if file and file.filename != '':
                filename = secure_filename(f"{email.split('@')[0]}_sig_{idx+1}.png")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                sig_sample = SignatureSample(user_id=new_user.id, filepath=filepath)
                db.session.add(sig_sample)
                saved_count += 1
                
        db.session.commit()
        flash(f'Successfully registered user with {saved_count} reference signature samples!', 'success')
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        file = request.files.get('signature')
        
        user = User.query.get(user_id)
        if not user or not user.signatures:
            flash('Selected user not found or has no reference samples on file.', 'danger')
            return redirect(url_for('verify'))
            
        if file and file.filename != '':
            test_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_temp.png')
            file.save(test_path)
            
            # Evaluate test signature against ALL reference samples and pick the highest score
            max_similarity = 0.0
            best_is_genuine = False
            
            for ref_sig in user.signatures:
                is_genuine, similarity_score = verify_signatures(
                    siamese_model, ref_sig.filepath, test_path
                )
                if similarity_score > max_similarity:
                    max_similarity = similarity_score
                    best_is_genuine = is_genuine
                    
            return render_template('verify_result.html', 
                                   user=user, 
                                   is_genuine=best_is_genuine, 
                                   score=round(max_similarity * 100, 2))
                                   
    users = User.query.all()
    return render_template('verify.html', users=users)


# ==========================================
# VERSIONED REST API ENDPOINTS (`/api/v1/...`)
# ==========================================
@app.route('/api/v1/users', methods=['GET'])
def api_get_users():
    """Fetch list of all registered users and their sample tracking count."""
    users = User.query.all()
    users_data = [{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "sample_count": len(u.signatures)
    } for u in users]
    return jsonify({"status": "success", "count": len(users_data), "users": users_data}), 200

@app.route('/api/v1/verify', methods=['POST'])
def api_verify_signature():
    """
    JSON / Multipart API endpoint for programmatic signature verification.
    Expects form-data: 'user_id' and file upload 'signature'.
    """
    user_id = request.form.get('user_id')
    file = request.files.get('signature')
    
    if not user_id or not file:
        return jsonify({"status": "error", "message": "Missing 'user_id' or 'signature' file payload."}), 400
        
    user = User.query.get(user_id)
    if not user or not user.signatures:
        return jsonify({"status": "error", "message": "User target not found or contains zero signature samples."}), 404
        
    try:
        test_path = os.path.join(app.config['UPLOAD_FOLDER'], 'api_test_temp.png')
        file.save(test_path)
        
        max_similarity = 0.0
        best_is_genuine = False
        
        for ref_sig in user.signatures:
            is_genuine, similarity_score = verify_signatures(
                siamese_model, ref_sig.filepath, test_path
            )
            if similarity_score > max_similarity:
                max_similarity = similarity_score
                best_is_genuine = is_genuine
                
        return jsonify({
            "status": "success",
            "user_id": user.id,
            "user_name": user.name,
            "is_genuine": bool(best_is_genuine),
            "similarity_percentage": round(max_similarity * 100, 2),
            "threshold_met": bool(max_similarity >= 0.75)
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)