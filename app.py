from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import sqlite3
import os
from collections import defaultdict
import calendar

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['DATABASE'] = 'kopi_makmur.db'

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
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with app.open_resource('schema.sql', mode='r') as f:
        conn.executescript(f.read())
    conn.commit()
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
            flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
            return redirect(url_for('cashflow_index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'username' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'viewonly':
            return redirect(url_for('viewonly'))
        else:
            return redirect(url_for('cashflow_index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check demo users first
        for user in DEMO_USERS:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                session['role'] = user['role']
                flash('Login berhasil!', 'success')
                return redirect(url_for('admin_dashboard'))
        
        # If not found in demo users, check database
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user['role']
            session['user_id'] = user['id']
            
            flash(f'Selamat datang, {username}!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'viewonly':
                return redirect(url_for('viewonly'))
            else:
                return redirect(url_for('cashflow_index'))
        else:
            flash('Username atau password salah', 'error')
    
    return render_template('login.html', demo_users=DEMO_USERS)

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout', 'success')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    
    # Get current month data
    now = datetime.now()
    start_date = now.replace(day=1).strftime('%Y-%m-%d')
    
    # Total revenue this month
    total_revenue = conn.execute(
        "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pendapatan' AND tanggal >= ?",
        (start_date,)
    ).fetchone()['total']
    
    # Total expense this month
    total_expense = conn.execute(
        "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ?",
        (start_date,)
    ).fetchone()['total']
    
    # Total transactions this month
    total_transactions = conn.execute(
        "SELECT COUNT(*) as total FROM transactions WHERE tanggal >= ?",
        (start_date,)
    ).fetchone()['total']
    
    # Recent transactions
    recent_transactions = conn.execute(
        "SELECT * FROM transactions ORDER BY tanggal DESC, id DESC LIMIT 10"
    ).fetchall()
    
    # Get last 6 months data for charts
    revenue_labels = []
    revenue_data = []
    expense_data = []
    profit_data = []
    
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30*i)
        month_name = month_date.strftime('%B')
        month_start = month_date.replace(day=1).strftime('%Y-%m-%d')
        
        # Calculate next month start
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1, day=1)
        else:
            next_month = month_date.replace(month=month_date.month + 1, day=1)
        month_end = next_month.strftime('%Y-%m-%d')
        
        revenue = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pendapatan' AND tanggal >= ? AND tanggal < ?",
            (month_start, month_end)
        ).fetchone()['total']
        
        expense = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ? AND tanggal < ?",
            (month_start, month_end)
        ).fetchone()['total']
        
        revenue_labels.append(month_name)
        revenue_data.append(float(revenue))
        expense_data.append(float(expense))
        profit_data.append(float(revenue - expense))
    
    # Category breakdown
    categories = conn.execute(
        "SELECT kategori, COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ? GROUP BY kategori",
        (start_date,)
    ).fetchall()
    
    category_labels = [cat['kategori'] for cat in categories]
    category_data = [float(cat['total']) for cat in categories]
    
    # Get user count
    user_count = conn.execute("SELECT COUNT(*) as total FROM users").fetchone()['total']
    
    conn.close()
    
    # Calculate additional metrics
    net_profit = total_revenue - total_expense
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return render_template('admin_dashboard.html',
                         total_revenue=total_revenue,
                         total_expense=total_expense,
                         total_transactions=total_transactions,
                         recent_transactions=recent_transactions,
                         revenue_labels=revenue_labels,
                         revenue_data=revenue_data,
                         expense_data=expense_data,
                         profit_data=profit_data,
                         category_labels=category_labels,
                         category_data=category_data,
                         net_profit=net_profit,
                         profit_margin=profit_margin,
                         total_users=user_count,
                         month_name=now.strftime('%B %Y'))

@app.route('/cashflow')
@login_required
def cashflow_index():
    conn = get_db_connection()
    
    # Get filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    month = request.args.get('month')
    year = request.args.get('year')
    
    # Build query
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if date_from:
        query += " AND tanggal >= ?"
        params.append(date_from)
    
    if date_to:
        query += " AND tanggal <= ?"
        params.append(date_to)
    
    if month:
        query += " AND strftime('%m', tanggal) = ?"
        params.append(f"{int(month):02d}")
    
    if year:
        query += " AND strftime('%Y', tanggal) = ?"
        params.append(year)
    
    query += " ORDER BY tanggal DESC, id DESC"
    
    transactions = conn.execute(query, params).fetchall()
    
    # Calculate totals
    total_pendapatan = sum([t['jumlah'] for t in transactions if t['tipe'] == 'pendapatan'])
    total_pengeluaran = sum([t['jumlah'] for t in transactions if t['tipe'] == 'pengeluaran'])
    
    # Get category breakdown
    category_summary = defaultdict(lambda: {'total_harga': 0, 'total_items': 0, 'total_quantity': '-'})
    
    for transaction in transactions:
        if transaction['tipe'] == 'pengeluaran':
            cat = transaction['kategori']
            category_summary[cat]['total_harga'] += transaction['jumlah']
            category_summary[cat]['total_items'] += 1
            
            # Calculate total quantity if kategori is "Bahan Pokok" or "Barang"
            if cat in ['Bahan Pokok', 'Barang'] and transaction.get('satuan') and transaction.get('jumlah'):
                quantity = transaction.get('jumlah', 0)
                unit = transaction.get('satuan', '')
                if category_summary[cat]['total_quantity'] == '-':
                    category_summary[cat]['total_quantity'] = f"{quantity} {unit}"
                else:
                    category_summary[cat]['total_quantity'] += f" + {quantity} {unit}"
    
    # Convert to list for template
    category_breakdown = []
    for kategori, data in category_summary.items():
        category_breakdown.append({
            'kategori': kategori,
            'total_harga': data['total_harga'],
            'total_items': data['total_items'],
            'total_quantity': data['total_quantity']
        })
    
    # Get monthly summary (current month)
    now = datetime.now()
    current_month = now.strftime('%m')
    current_year = now.strftime('%Y')
    
    monthly_transactions = conn.execute(
        "SELECT * FROM transactions WHERE strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?",
        (current_month, current_year)
    ).fetchall()
    
    monthly_revenue = sum([t['jumlah'] for t in monthly_transactions if t['tipe'] == 'pendapatan'])
    monthly_expense = sum([t['jumlah'] for t in monthly_transactions if t['tipe'] == 'pengeluaran'])
    monthly_transactions_count = len(monthly_transactions)
    
    conn.close()
    
    # Month name for display
    month_names = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    return render_template('cashflow_index.html',
                         transactions=transactions,
                         total_pendapatan=total_pendapatan,
                         total_pengeluaran=total_pengeluaran,
                         category_breakdown=category_breakdown,
                         monthly_revenue=monthly_revenue,
                         monthly_expense=monthly_expense,
                         monthly_transactions_count=monthly_transactions_count,
                         current_month=now.strftime('%B %Y'),
                         month_names=month_names)

@app.route('/cashflow/add', methods=['POST'])
@login_required
def add_transaction():
    tanggal = request.form['tanggal']
    tipe = request.form['tipe']
    kategori = request.form['kategori']
    deskripsi = request.form['deskripsi']
    jumlah = request.form['jumlah']
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO transactions (tanggal, tipe, kategori, deskripsi, jumlah, user_id) VALUES (?, ?, ?, ?, ?, ?)',
        (tanggal, tipe, kategori, deskripsi, jumlah, session['user_id'])
    )
    conn.commit()
    conn.close()
    
    flash('Transaksi berhasil ditambahkan', 'success')
    return redirect(url_for('cashflow_index'))

@app.route('/cashflow/edit/<int:id>')
@login_required
def edit_transaksi(id):
    conn = get_db_connection()
    transaction = conn.execute('SELECT * FROM transactions WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if not transaction:
        flash('Transaksi tidak ditemukan', 'error')
        return redirect(url_for('cashflow_index'))
    
    return render_template('edit_transaksi.html', transaction=transaction)

@app.route('/cashflow/update/<int:id>', methods=['POST'])
@login_required
def update_transaksi(id):
    tanggal = request.form['tanggal']
    tipe = request.form['tipe']
    kategori = request.form['kategori']
    deskripsi = request.form['deskripsi']
    jumlah = request.form['jumlah']
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE transactions SET tanggal=?, tipe=?, kategori=?, deskripsi=?, jumlah=? WHERE id=?',
        (tanggal, tipe, kategori, deskripsi, jumlah, id)
    )
    conn.commit()
    conn.close()
    
    flash('Transaksi berhasil diupdate', 'success')
    return redirect(url_for('cashflow_index'))

@app.route('/delete_transaction/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM transactions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/laporan')
@login_required
def laporan_cashflow():
    conn = get_db_connection()
    
    # Get filter parameters
    month = request.args.get('month')
    year = request.args.get('year', datetime.now().year)
    
    # Build query
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if month:
        query += " AND strftime('%m', tanggal) = ?"
        params.append(f"{int(month):02d}")
    
    if year:
        query += " AND strftime('%Y', tanggal) = ?"
        params.append(str(year))
    
    query += " ORDER BY tanggal DESC"
    
    transactions = conn.execute(query, params).fetchall()
    
    # Calculate totals
    total_revenue = sum([t['jumlah'] for t in transactions if t['tipe'] == 'pendapatan'])
    total_expense = sum([t['jumlah'] for t in transactions if t['tipe'] == 'pengeluaran'])
    
    # Prepare chart data
    chart_labels = []
    revenue_data = []
    expense_data = []
    
    if month:
        # Daily data for the month
        _, num_days = calendar.monthrange(int(year), int(month))
        for day in range(1, num_days + 1):
            date_str = f"{year}-{int(month):02d}-{day:02d}"
            chart_labels.append(str(day))
            
            revenue = sum([t['jumlah'] for t in transactions if t['tanggal'] == date_str and t['tipe'] == 'pendapatan'])
            expense = sum([t['jumlah'] for t in transactions if t['tanggal'] == date_str and t['tipe'] == 'pengeluaran'])
            
            revenue_data.append(float(revenue))
            expense_data.append(float(expense))
    else:
        # Monthly data for the year
        for m in range(1, 13):
            month_name = calendar.month_name[m][:3]
            chart_labels.append(month_name)
            
            month_transactions = [t for t in transactions if int(t['tanggal'].split('-')[1]) == m]
            revenue = sum([t['jumlah'] for t in month_transactions if t['tipe'] == 'pendapatan'])
            expense = sum([t['jumlah'] for t in month_transactions if t['tipe'] == 'pengeluaran'])
            
            revenue_data.append(float(revenue))
            expense_data.append(float(expense))
    
    # Category breakdown
    categories = defaultdict(float)
    for t in transactions:
        if t['tipe'] == 'pengeluaran':
            categories[t['kategori']] += t['jumlah']
    
    category_labels = list(categories.keys())
    category_data = [float(v) for v in categories.values()]
    
    conn.close()
    
    # Month names for display
    month_names = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    return render_template('laporan_cashflow.html',
                         transactions=transactions,
                         total_revenue=total_revenue,
                         total_expense=total_expense,
                         chart_labels=chart_labels,
                         revenue_data=revenue_data,
                         expense_data=expense_data,
                         category_labels=category_labels,
                         category_data=category_data,
                         month_names=month_names,
                         selected_bulan=int(month) if month else datetime.now().month,
                         selected_tahun=int(year) if year else datetime.now().year)

@app.route('/viewonly')
@login_required
def viewonly():
    if session.get('role') != 'viewonly':
        return redirect(url_for('cashflow_index'))
    
    conn = get_db_connection()
    
    # Get current month data
    now = datetime.now()
    start_date = now.replace(day=1).strftime('%Y-%m-%d')
    
    # Total revenue this month
    total_revenue = conn.execute(
        "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pendapatan' AND tanggal >= ?",
        (start_date,)
    ).fetchone()['total']
    
    # Total expense this month
    total_expense = conn.execute(
        "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ?",
        (start_date,)
    ).fetchone()['total']
    
    # Recent transactions
    recent_transactions = conn.execute(
        "SELECT * FROM transactions ORDER BY tanggal DESC, id DESC LIMIT 10"
    ).fetchall()
    
    # Get last 6 months data for charts
    revenue_labels = []
    revenue_data = []
    expense_data = []
    
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30*i)
        month_name = month_date.strftime('%B')
        month_start = month_date.replace(day=1).strftime('%Y-%m-%d')
        
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1, day=1)
        else:
            next_month = month_date.replace(month=month_date.month + 1, day=1)
        month_end = next_month.strftime('%Y-%m-%d')
        
        revenue = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pendapatan' AND tanggal >= ? AND tanggal < ?",
            (month_start, month_end)
        ).fetchone()['total']
        
        expense = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ? AND tanggal < ?",
            (month_start, month_end)
        ).fetchone()['total']
        
        revenue_labels.append(month_name)
        revenue_data.append(float(revenue))
        expense_data.append(float(expense))
    
    # Category breakdown
    categories = conn.execute(
        "SELECT kategori, COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ? GROUP BY kategori",
        (start_date,)
    ).fetchall()
    
    category_labels = [cat['kategori'] for cat in categories]
    category_data = [float(cat['total']) for cat in categories]
    
    # Get user count
    total_users = conn.execute("SELECT COUNT(*) as total FROM users").fetchone()['total']
    
    conn.close()
    
    # Calculate net profit
    net_profit = total_revenue - total_expense
    
    return render_template('viewonly.html',
                         total_revenue=total_revenue,
                         total_expense=total_expense,
                         net_profit=net_profit,
                         total_users=total_users,
                         recent_transactions=recent_transactions,
                         revenue_labels=revenue_labels,
                         revenue_data=revenue_data,
                         expense_data=expense_data,
                         category_labels=category_labels,
                         category_data=category_data,
                         month_name=now.strftime('%B %Y'))

# User Management Routes
@app.route('/users')
@login_required
@admin_required
def manajemen_user():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY id').fetchall()
    total_users_count = len(users)
    conn.close()
    
    return render_template('manajemen_user.html', users=users, total_users_count=total_users_count)

@app.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            (username, hashed_password, role)
        )
        conn.commit()
        flash(f'User {username} berhasil ditambahkan', 'success')
    except sqlite3.IntegrityError:
        flash(f'Username {username} sudah ada', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('manajemen_user'))

@app.route('/users/edit', methods=['POST'])
@login_required
@admin_required
def edit_user():
    user_id = request.form['user_id']
    username = request.form['username']
    password = request.form.get('password')
    role = request.form['role']
    
    conn = get_db_connection()
    
    if password:
        hashed_password = generate_password_hash(password)
        conn.execute(
            'UPDATE users SET username=?, password=?, role=? WHERE id=?',
            (username, hashed_password, role, user_id)
        )
    else:
        conn.execute(
            'UPDATE users SET username=?, role=? WHERE id=?',
            (username, role, user_id)
        )
    
    conn.commit()
    conn.close()
    
    flash('User berhasil diupdate', 'success')
    return redirect(url_for('manajemen_user'))

@app.route('/delete_user/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if id == session['user_id']:
        return jsonify({'success': False, 'message': 'Tidak dapat menghapus user sendiri'})
    
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Product Management Routes
@app.route('/products')
@login_required
@admin_required
def manajemen_product():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id').fetchall()
    total_products_count = len(products)
    conn.close()
    
    return render_template('manajemen_product.html', products=products, total_products_count=total_products_count)

@app.route('/products/add', methods=['POST'])
@login_required
@admin_required
def add_product():
    nama = request.form['nama']
    kategori = request.form['kategori']
    harga = request.form['harga']
    stok = request.form['stok']
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO products (nama, kategori, harga, stok) VALUES (?, ?, ?, ?)',
        (nama, kategori, harga, stok)
    )
    conn.commit()
    conn.close()
    
    flash(f'Produk {nama} berhasil ditambahkan', 'success')
    return redirect(url_for('manajemen_product'))

@app.route('/products/edit', methods=['POST'])
@login_required
@admin_required
def edit_product():
    product_id = request.form['product_id']
    nama = request.form['nama']
    kategori = request.form['kategori']
    harga = request.form['harga']
    stok = request.form['stok']
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE products SET nama=?, kategori=?, harga=?, stok=? WHERE id=?',
        (nama, kategori, harga, stok, product_id)
    )
    conn.commit()
    conn.close()
    
    flash('Produk berhasil diupdate', 'success')
    return redirect(url_for('manajemen_product'))

@app.route('/delete_product/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Export routes (placeholder)
@app.route('/export/pdf')
@login_required
def export_pdf():
    flash('Fitur export PDF akan segera tersedia', 'info')
    return redirect(url_for('laporan_cashflow'))

@app.route('/export/excel')
@login_required
def export_excel():
    flash('Fitur export Excel akan segera tersedia', 'info')
    return redirect(url_for('laporan_cashflow'))

# API endpoints for dynamic data
@app.route('/api/expense-distribution')
@login_required
def api_expense_distribution():
    """API endpoint untuk data distribusi pengeluaran"""
    conn = get_db_connection()
    
    # Get current month data
    now = datetime.now()
    start_date = now.replace(day=1).strftime('%Y-%m-%d')
    
    # Category breakdown
    categories = conn.execute(
        "SELECT kategori, COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ? GROUP BY kategori ORDER BY total DESC",
        (start_date,)
    ).fetchall()
    
    if not categories:
        # Return default sample data if no real data
        return jsonify({
            'labels': ['Bahan Pokok', 'Barang', 'Pengeluaran lain_lain'],
            'data': [90.9, 5.3, 3.8]
        })
    
    labels = [cat['kategori'] for cat in categories]
    data = [float(cat['total']) for cat in categories]
    
    conn.close()
    
    return jsonify({
        'labels': labels,
        'data': data
    })

@app.route('/api/cashflow-trend')
@login_required
def api_cashflow_trend():
    """API endpoint untuk data trend cashflow"""
    conn = get_db_connection()
    
    # Get last 6 months data
    now = datetime.now()
    labels = []
    revenue_data = []
    expense_data = []
    
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30*i)
        month_name = month_date.strftime('%B %Y')
        month_start = month_date.replace(day=1).strftime('%Y-%m-%d')
        
        # Calculate next month start
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1, day=1)
        else:
            next_month = month_date.replace(month=month_date.month + 1, day=1)
        month_end = next_month.strftime('%Y-%m-%d')
        
        revenue = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pendapatan' AND tanggal >= ? AND tanggal < ?",
            (month_start, month_end)
        ).fetchone()['total']
        
        expense = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ? AND tanggal < ?",
            (month_start, month_end)
        ).fetchone()['total']
        
        labels.append(month_name)
        revenue_data.append(float(revenue))
        expense_data.append(float(expense))
    
    conn.close()
    
    return jsonify({
        'labels': labels,
        'revenue': revenue_data,
        'expense': expense_data
    })

@app.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint untuk statistik dashboard"""
    conn = get_db_connection()
    
    # Get current month data
    now = datetime.now()
    start_date = now.replace(day=1).strftime('%Y-%m-%d')
    
    # Total revenue this month
    total_revenue = conn.execute(
        "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pendapatan' AND tanggal >= ?",
        (start_date,)
    ).fetchone()['total']
    
    # Total expense this month
    total_expense = conn.execute(
        "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ?",
        (start_date,)
    ).fetchone()['total']
    
    # Total transactions this month
    total_transactions = conn.execute(
        "SELECT COUNT(*) as total FROM transactions WHERE tanggal >= ?",
        (start_date,)
    ).fetchone()['total']
    
    # Total users
    total_users = conn.execute("SELECT COUNT(*) as total FROM users").fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'total_revenue': float(total_revenue),
        'total_expense': float(total_expense),
        'total_transactions': int(total_transactions),
        'total_users': int(total_users),
        'profit': float(total_revenue - total_expense)
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    if not os.path.exists(app.config['DATABASE']):
        print("Database not found. Please run init_db.py first.")
    app.run(debug=True, host='0.0.0.0', port=5000)
