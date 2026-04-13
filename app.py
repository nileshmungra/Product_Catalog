from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Product
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"   # change to a secure random key

# --- Database Config ---
# Use PostgreSQL if DATABASE_URL is set (Render), otherwise fallback to SQLite (local)
db_url = os.environ.get("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
db.init_app(app)

with app.app_context():
    db.create_all()

# --- Authentication ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":  # set your credentials
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# --- Admin Dashboard ---
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))
    products = Product.query.all()
    return render_template('admin.html', products=products)

# --- User Dashboard ---
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
    image = request.files['image']
    filename = image.filename
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    product = Product(name=name, code=code, image=filename)
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
    if 'image' in request.files and request.files['image'].filename:
        image = request.files['image']
        filename = image.filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        product.image = filename
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
