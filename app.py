from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Product
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
load_dotenv()  # Aa line .env file mathi keys load kari leshe

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "any-random-string-for-local")

# --- Cloudinary Configuration ---
# Render na 'Environment Variables' ma je Key names aapya hoy e j aya lakhva
cloudinary.config( 
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
    api_key = os.environ.get('CLOUDINARY_API_KEY'), 
    api_secret = os.environ.get('CLOUDINARY_API_SECRET') 
)

# --- Database Config ---
db_url = os.environ.get("DATABASE_URL")
if db_url:
    # Render na PostgreSQL mate 'postgres://' ne 'postgresql://' ma badalvu jaruri che
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# --- Authentication ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# --- Admin & User Dashboards ---
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/')
def user_dashboard():
    products = Product.query.all()
    return render_template('user.html', products=products)

# --- CRUD routes ---
@app.route('/add', methods=['POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    name = request.form['name']
    code = request.form['code']
    image_file = request.files['image']
    
    if image_file:
        # 1. Image ne Cloudinary par upload karo
        upload_result = cloudinary.uploader.upload(image_file)
        # 2. Local filename ni jagya e permanent URL medvo
        image_url = upload_result['secure_url']
        
        product = Product(name=name, code=code, image=image_url)
        db.session.add(product)
        db.session.commit()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/update/<int:id>', methods=['POST'])
def update_product(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    product = Product.query.get(id)
    product.name = request.form['name']
    product.code = request.form['code']
    
    if 'image' in request.files and request.files['image'].filename != '':
        image_file = request.files['image']
        # Navi image Cloudinary par upload karo
        upload_result = cloudinary.uploader.upload(image_file)
        product.image = upload_result['secure_url']
        
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete/<int:id>')
def delete_product(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)