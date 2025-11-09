from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import sqlite3
import os
from collections import defaultdict
import calendar
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Production configuration
app = Flask(__name__)

# Environment-based configuration
if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
else:
    app.config['DEBUG'] = True
    app.config['TESTING'] = True

# Security configurations
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database configuration - supports both SQLite and cloud databases
def get_database_path():
    # Support for both local and cloud deployments
    if os.getenv('DATABASE_URL'):
        return os.getenv('DATABASE_URL')
    elif os.getenv('HEROKU_POSTGRESQL_URL'):
        return os.getenv('HEROKU_POSTGRESQL_URL')
    else:
        # Local development fallback
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kopi_makmur.db')

app.config['DATABASE'] = get_database_path()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configure logging for production
if not app.config['DEBUG']:
    logging.basicConfig(level=logging.INFO)

# Demo data for login page
DEMO_USERS = [
    {'username': 'BagasNz', 'password': '162316', 'role': 'admin'},
    {'username': 'Refki', 'password': 'owner', 'role': 'guest'},
    {'username': 'Iqbal', 'password': 'owner', 'role': 'guest'},
    {'username': 'Rico', 'password': 'owner', 'role': 'guest'},
    {'username': 'Hari', 'password': 'owner', 'role': 'guest'},
    {'username': 'Dimse', 'password': 'owner', 'role': 'guest'},
]

# Database helper functions
def get_db_connection():
    try:
        # Try SQLite first
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as e:
        app.logger.error(f"Database connection error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with app.open_resource('schema.sql', mode='r') as f:
            conn.executescript(f.read())
        conn.commit()
        return True
    except Exception as e:
        app.logger.error(f"Database initialization error: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Silakan login terlebih dahulu', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            flash('Akses admin diperlukan', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check demo users
        for user in DEMO_USERS:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                session['role'] = user['role']
                flash('Login berhasil!', 'success')
                return redirect(url_for('admin_dashboard'))
        
        flash('Username atau password salah', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Berhasil logout', 'success')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error', 'error')
        return redirect(url_for('login'))
    
    try:
        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Total revenue
        total_revenue = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pendapatan' AND tanggal >= ?",
            (start_date,)
        ).fetchone()['total']
        
        # Total expense
        total_expense = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ?",
            (start_date,)
        ).fetchone()['total']
        
        # Total transactions
        total_transactions = conn.execute(
            "SELECT COUNT(*) as total FROM transactions WHERE tanggal >= ?",
            (start_date,)
        ).fetchone()['total']
        
        # Recent transactions
        recent_transactions = conn.execute(
            "SELECT * FROM transactions ORDER BY tanggal DESC LIMIT 10"
        ).fetchall()
        
        # Products summary
        products_summary = conn.execute(
            "SELECT nama, kategori, harga FROM products ORDER BY kategori, nama"
        ).fetchall()
        
        conn.close()
        
        profit_margin = ((total_revenue - total_expense) / total_revenue * 100) if total_revenue > 0 else 0
        
        return render_template('admin_dashboard.html',
                             total_revenue=total_revenue,
                             total_expense=total_expense,
                             profit_margin=profit_margin,
                             total_transactions=total_transactions,
                             recent_transactions=recent_transactions,
                             products_summary=products_summary)
    
    except Exception as e:
        app.logger.error(f"Dashboard error: {e}")
        flash('Error loading dashboard data', 'error')
        return redirect(url_for('login'))

# API endpoints for dashboard data
@app.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection error'}), 500
    
    try:
        # Calculate date range (current month)
        end_date = datetime.now()
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get current month stats
        total_revenue = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pendapatan' AND tanggal >= ?",
            (start_date,)
        ).fetchone()['total']
        
        total_expense = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ?",
            (start_date,)
        ).fetchone()['total']
        
        total_transactions = conn.execute(
            "SELECT COUNT(*) as total FROM transactions WHERE tanggal >= ?",
            (start_date,)
        ).fetchone()['total']
        
        total_users = conn.execute("SELECT COUNT(*) as total FROM users").fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'total_revenue': float(total_revenue),
            'total_expense': float(total_expense),
            'total_transactions': int(total_transactions),
            'total_users': int(total_users),
            'profit': float(total_revenue - total_expense)
        })
    
    except Exception as e:
        app.logger.error(f"API stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    if not app.config.get('TESTING'):
        app.logger.warning(f"404 error: {request.path}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    if not app.config.get('TESTING'):
        app.logger.error(f"500 error: {error}")
    return render_template('500.html'), 500

# Health check endpoint for deployment platforms
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if app.config['DEBUG']:
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        # Production server
        from gunicorn.app.wsgiapp import WSGIApplication
        application = WSGIApplication("0.0.0.0:{}".format(port), app)
        application.run()