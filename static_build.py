#!/usr/bin/env python3
"""
Static Build Generator for Toko Kopi Makmur
This script generates a static version of the Flask app for Netlify deployment
"""

import os
import shutil
import sqlite3
from jinja2 import Template
import json
from datetime import datetime, timedelta

def build_static_version():
    """Generate static HTML files from Flask templates"""
    
    print("🏗️ Building static version of Toko Kopi Makmur...")
    
    # Create dist directory
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Create subdirectories
    os.makedirs(f"{dist_dir}/static/css")
    os.makedirs(f"{dist_dir}/static/js")
    os.makedirs(f"{dist_dir}/static/images")
    os.makedirs(f"{dist_dir}/api")
    
    # Read database
    try:
        conn = sqlite3.connect('kopi_makmur.db')
        conn.row_factory = sqlite3.Row
        
        # Get dashboard data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        total_revenue = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pendapatan' AND tanggal >= ?",
            (start_date,)
        ).fetchone()['total']
        
        total_expense = conn.execute(
            "SELECT COALESCE(SUM(jumlah), 0) as total FROM transactions WHERE tipe = 'pengeluaran' AND tanggal >= ?",
            (start_date,)
        ).fetchone()['total']
        
        recent_transactions = conn.execute(
            "SELECT * FROM transactions ORDER BY tanggal DESC LIMIT 10"
        ).fetchall()
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Database error: {e}")
        # Use default values if database is not available
        total_revenue = 0
        total_expense = 0
        recent_transactions = []
    
    # Copy static files
    try:
        if os.path.exists("static"):
            shutil.copytree("static", f"{dist_dir}/static", dirs_exist_ok=True)
    except Exception as e:
        print(f"⚠️ Static files copy error: {e}")
    
    # Generate sample data for static version
    sample_data = {
        "total_revenue": total_revenue,
        "total_expense": total_expense,
        "profit": total_revenue - total_expense,
        "profit_margin": ((total_revenue - total_expense) / total_revenue * 100) if total_revenue > 0 else 0,
        "total_transactions": len(recent_transactions),
        "recent_transactions": [dict(row) for row in recent_transactions]
    }
    
    # Generate static pages
    generate_index_page(dist_dir, sample_data)
    generate_dashboard_page(dist_dir, sample_data)
    generate_api_endpoints(dist_dir, sample_data)
    generate_404_page(dist_dir)
    
    print(f"✅ Static version built successfully in '{dist_dir}/' directory")
    print(f"📁 Open {dist_dir}/index.html in your browser to view")
    
    return dist_dir

def generate_index_page(dist_dir, data):
    """Generate static index page"""
    
    index_html = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toko Kopi Makmur - Sistem Manajemen</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
            color: white;
            padding: 100px 0;
        }
        .feature-card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .feature-card:hover {
            transform: translateY(-10px);
        }
        .metric-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: none;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #8B4513;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-coffee me-2"></i>
                Toko Kopi Makmur
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link active" href="#dashboard">Dashboard</a>
                <a class="nav-link" href="#features">Fitur</a>
                <a class="nav-link" href="#about">Tentang</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6">
                    <h1 class="display-4 mb-4">Sistem Manajemen Toko Kopi</h1>
                    <p class="lead mb-4">Kelola transaksi, keuangan, dan inventori toko kopi Anda dengan mudah dan efisien.</p>
                    <a href="#dashboard" class="btn btn-light btn-lg me-3">
                        <i class="fas fa-chart-line me-2"></i>Lihat Dashboard
                    </a>
                    <a href="#features" class="btn btn-outline-light btn-lg">
                        <i class="fas fa-star me-2"></i>Pelajari Fitur
                    </a>
                </div>
                <div class="col-lg-6">
                    <img src="/static/images/logo1.jpg" alt="Toko Kopi" class="img-fluid rounded" style="max-height: 400px;">
                </div>
            </div>
        </div>
    </section>

    <!-- Dashboard Section -->
    <section id="dashboard" class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">Dashboard Keuangan</h2>
            <div class="row">
                <div class="col-md-3 mb-4">
                    <div class="metric-card">
                        <i class="fas fa-chart-line fa-2x text-success mb-3"></i>
                        <h5>Total Pendapatan</h5>
                        <div class="metric-value">Rp {{ "{:,.0f}".format(data.total_revenue) }}</div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="metric-card">
                        <i class="fas fa-chart-pie fa-2x text-danger mb-3"></i>
                        <h5>Total Pengeluaran</h5>
                        <div class="metric-value">Rp {{ "{:,.0f}".format(data.total_expense) }}</div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="metric-card">
                        <i class="fas fa-money-bill-trend-up fa-2x text-info mb-3"></i>
                        <h5>Laba Bersih</h5>
                        <div class="metric-value">Rp {{ "{:,.0f}".format(data.profit) }}</div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="metric-card">
                        <i class="fas fa-percentage fa-2x text-warning mb-3"></i>
                        <h5>Margin Laba</h5>
                        <div class="metric-value">{{ "%.1f"|format(data.profit_margin) }}%</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-5 bg-light">
        <div class="container">
            <h2 class="text-center mb-5">Fitur Unggulan</h2>
            <div class="row">
                <div class="col-lg-4 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-cash-register fa-3x text-primary mb-3"></i>
                            <h5>Manajemen Transaksi</h5>
                            <p>Catat semua transaksi penjualan dan pembelian dengan mudah dan akurat.</p>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-chart-bar fa-3x text-success mb-3"></i>
                            <h5>Laporan Keuangan</h5>
                            <p>Generate laporan keuangan lengkap dengan analisis profit dan cash flow.</p>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-boxes fa-3x text-info mb-3"></i>
                            <h5>Manajemen Produk</h5>
                            <p>Kelola inventori produk, kategori, dan harga dengan sistem yang terorganisir.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-5">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 mx-auto text-center">
                    <h2 class="mb-4">Tentang Sistem Ini</h2>
                    <p class="lead">Sistem Manajemen Toko Kopi Makmur adalah solusi lengkap untuk membantu Anda mengelola operasional toko kopi dengan lebih efisien. Dengan fitur-fitur yang mudah digunakan, Anda dapat fokus pada bisnis tanpa terkendala masalah administrasi.</p>
                    <div class="mt-4">
                        <a href="#" class="btn btn-primary btn-lg me-3" onclick="showLogin()">
                            <i class="fas fa-sign-in-alt me-2"></i>Masuk ke Sistem
                        </a>
                        <a href="mailto:support@kopimakmur.com" class="btn btn-outline-primary btn-lg">
                            <i class="fas fa-envelope me-2"></i>Hubungi Kami
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p class="mb-0">&copy; 2024 Toko Kopi Makmur. All rights reserved.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <p class="mb-0">Developed by MiniMax Agent</p>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showLogin() {
            alert('Untuk mengakses sistem lengkap, mohon deploy ke platform yang mendukung Flask/Python seperti Heroku, Railway, atau Render.');
        }
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>"""
    
    # Render template with data
    template = Template(index_html)
    html_content = template.render(data=data)
    
    with open(f"{dist_dir}/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_dashboard_page(dist_dir, data):
    """Generate static dashboard page"""
    
    dashboard_html = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Toko Kopi Makmur</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar {
            min-height: 100vh;
            background: linear-gradient(180deg, #8B4513 0%, #654321 100%);
        }
        .sidebar .nav-link {
            color: rgba(255,255,255,0.8);
            padding: 15px 20px;
            margin: 5px 0;
            border-radius: 10px;
        }
        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            background: rgba(255,255,255,0.1);
            color: white;
        }
        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-left: 4px solid;
        }
        .metric-revenue { border-left-color: #28a745; }
        .metric-expense { border-left-color: #dc3545; }
        .metric-profit { border-left-color: #17a2b8; }
        .metric-margin { border-left-color: #ffc107; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3 p-0">
                <div class="sidebar text-white p-4">
                    <h3 class="mb-4">
                        <i class="fas fa-coffee me-2"></i>
                        Toko Kopi Makmur
                    </h3>
                    <nav class="nav flex-column">
                        <a class="nav-link active" href="#">
                            <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                        </a>
                        <a class="nav-link" href="#">
                            <i class="fas fa-cash-register me-2"></i>Transaksi
                        </a>
                        <a class="nav-link" href="#">
                            <i class="fas fa-chart-line me-2"></i>Laporan
                        </a>
                        <a class="nav-link" href="#">
                            <i class="fas fa-boxes me-2"></i>Produk
                        </a>
                        <a class="nav-link" href="#">
                            <i class="fas fa-users me-2"></i>User Management
                        </a>
                    </nav>
                </div>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-9">
                <div class="p-4">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h1>Dashboard</h1>
                        <span class="badge bg-primary">30 Hari Terakhir</span>
                    </div>
                    
                    <!-- Metrics Row -->
                    <div class="row mb-4">
                        <div class="col-md-3 mb-3">
                            <div class="metric-card metric-revenue">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="text-muted">Total Pendapatan</h6>
                                        <h3 class="text-success">Rp {{ "{:,.0f}".format(data.total_revenue) }}</h3>
                                    </div>
                                    <i class="fas fa-chart-line fa-2x text-success opacity-75"></i>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="metric-card metric-expense">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="text-muted">Total Pengeluaran</h6>
                                        <h3 class="text-danger">Rp {{ "{:,.0f}".format(data.total_expense) }}</h3>
                                    </div>
                                    <i class="fas fa-chart-pie fa-2x text-danger opacity-75"></i>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="metric-card metric-profit">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="text-muted">Laba Bersih</h6>
                                        <h3 class="text-info">Rp {{ "{:,.0f}".format(data.profit) }}</h3>
                                    </div>
                                    <i class="fas fa-money-bill-trend-up fa-2x text-info opacity-75"></i>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3 mb-3">
                            <div class="metric-card metric-margin">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="text-muted">Margin Laba</h6>
                                        <h3 class="text-warning">{{ "%.1f"|format(data.profit_margin) }}%</h3>
                                    </div>
                                    <i class="fas fa-percentage fa-2x text-warning opacity-75"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Charts Row -->
                    <div class="row mb-4">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">Cash Flow Trend</h5>
                                </div>
                                <div class="card-body">
                                    <div class="text-center py-5">
                                        <i class="fas fa-chart-line fa-4x text-muted mb-3"></i>
                                        <p class="text-muted">Chart akan muncul di versi dinamis</p>
                                        <small class="text-muted">Deploy ke platform Python untuk melihat chart interaktif</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">Expense Distribution</h5>
                                </div>
                                <div class="card-body">
                                    <div class="text-center py-5">
                                        <i class="fas fa-chart-pie fa-4x text-muted mb-3"></i>
                                        <p class="text-muted">Pie chart akan muncul di versi dinamis</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recent Transactions -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Transaksi Terbaru</h5>
                        </div>
                        <div class="card-body">
                            {% if data.recent_transactions %}
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Tanggal</th>
                                            <th>Deskripsi</th>
                                            <th>Jumlah</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for transaction in data.recent_transactions[:5] %}
                                        <tr>
                                            <td>{{ transaction.tanggal }}</td>
                                            <td>{{ transaction.deskripsi[:30] }}...</td>
                                            <td>Rp {{ "{:,.0f}".format(transaction.jumlah) }}</td>
                                            <td>
                                                <span class="badge bg-{{ 'success' if transaction.tipe == 'pendapatan' else 'danger' }}">
                                                    {{ 'Pemasukan' if transaction.tipe == 'pendapatan' else 'Pengeluaran' }}
                                                </span>
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                            {% else %}
                            <div class="text-center py-5">
                                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                                <p class="text-muted">Belum ada transaksi</p>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    # Render template with data
    template = Template(dashboard_html)
    html_content = template.render(data=data)
    
    with open(f"{dist_dir}/dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_api_endpoints(dist_dir, data):
    """Generate static API endpoints"""
    
    # Dashboard stats API
    stats_api = {
        "total_revenue": float(data["total_revenue"]),
        "total_expense": float(data["total_expense"]),
        "total_transactions": data["total_transactions"],
        "profit": float(data["profit"]),
        "margin": float(data["profit_margin"])
    }
    
    with open(f"{dist_dir}/api/dashboard-stats.json", "w") as f:
        json.dump(stats_api, f, indent=2)
    
    # Recent transactions API
    transactions_api = {
        "recent_transactions": data["recent_transactions"]
    }
    
    with open(f"{dist_dir}/api/recent-transactions.json", "w") as f:
        json.dump(transactions_api, f, indent=2, default=str)

def generate_404_page(dist_dir):
    """Generate 404 error page"""
    
    error_404 = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Halaman Tidak Ditemukan - Toko Kopi Makmur</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="row justify-content-center align-items-center" style="min-height: 100vh;">
            <div class="col-md-6 text-center">
                <div class="error-content">
                    <i class="fas fa-exclamation-triangle fa-5x text-warning mb-4"></i>
                    <h1 class="display-1 fw-bold text-muted">404</h1>
                    <h2 class="mb-4">Halaman Tidak Ditemukan</h2>
                    <p class="lead text-muted mb-4">
                        Maaf, halaman yang Anda cari tidak ditemukan.<br>
                        Halaman ini mungkin telah dipindahkan atau tidak ada.
                    </p>
                    <a href="/" class="btn btn-primary btn-lg">
                        <i class="fas fa-home me-2"></i>Kembali ke Beranda
                    </a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with open(f"{dist_dir}/404.html", "w", encoding="utf-8") as f:
        f.write(error_404)

if __name__ == "__main__":
    build_static_version()