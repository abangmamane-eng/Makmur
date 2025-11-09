#!/usr/bin/env python3
"""
Database Initialization Script for Toko Kopi Makmur
This script creates the database and populates it with sample data
"""

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

DATABASE = 'kopi_makmur.db'

def init_database():
    """Initialize database with schema and sample data"""
    
    print("🔧 Initializing database...")
    
    # Connect to database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Read and execute schema
    print("📋 Creating tables...")
    with open('schema.sql', 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    # Insert sample users
    print("👥 Creating sample users...")
    users = [
        ('BagasNz', '162316', 'admin'),
        ('Refki', 'owner', 'user'),
        ('Iqbal', 'owner', 'user'),
        ('Rico', 'owner', 'user'),
        ('Hari', 'owner', 'user'),
        ('Dimse', 'owner', 'user'),
    ]
    
    for username, password, role in users:
        hashed_password = generate_password_hash(password)
        try:
            cursor.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (username, hashed_password, role)
            )
            print(f"   ✓ Created user: {username} (password: {password}, role: {role})")
        except sqlite3.IntegrityError:
            print(f"   - User {username} already exists")
    
    # Insert sample products
    print("📦 Creating sample products...")
    products = [
        ('Kopi Arabica', 'Kopi', 25000, 50),
        ('Kopi Robusta', 'Kopi', 20000, 40),
        ('Cappuccino', 'Minuman', 30000, 30),
        ('Latte', 'Minuman', 32000, 25),
        ('Espresso', 'Minuman', 22000, 35),
        ('Croissant', 'Makanan', 15000, 20),
        ('Roti Bakar', 'Makanan', 12000, 15),
        ('Donat', 'Snack', 8000, 40),
        ('Cookies', 'Snack', 10000, 30),
    ]
    
    for nama, kategori, harga, stok in products:
        try:
            cursor.execute(
                'INSERT INTO products (nama, kategori, harga, stok) VALUES (?, ?, ?, ?)',
                (nama, kategori, harga, stok)
            )
            print(f"   ✓ Added product: {nama}")
        except sqlite3.IntegrityError:
            print(f"   - Product {nama} already exists")
    
    # Insert sample transactions (last 3 months)
    print("💰 Creating sample transactions...")
    
    categories_pendapatan = ['Penjualan']
    categories_pengeluaran = ['Bahan Pokok', 'Barang', 'Jasa', 'Pengeluaran lain-lain']
    
    # Get admin user id
    admin_id = cursor.execute("SELECT id FROM users WHERE username = 'BagasNz'").fetchone()[0]
    
    # Generate transactions for the last 90 days
    start_date = datetime.now() - timedelta(days=90)
    transaction_count = 0
    
    for day_offset in range(90):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Generate 2-5 transactions per day
        num_transactions = random.randint(2, 5)
        
        for _ in range(num_transactions):
            # Random choice between pendapatan and pengeluaran (60% pendapatan, 40% pengeluaran)
            tipe = 'pendapatan' if random.random() < 0.6 else 'pengeluaran'
            
            if tipe == 'pendapatan':
                kategori = random.choice(categories_pendapatan)
                jumlah = random.randint(50, 500) * 1000  # 50k - 500k
                deskripsi = f"Penjualan {random.choice(['Kopi', 'Makanan', 'Minuman', 'Paket'])}"
            else:
                kategori = random.choice(categories_pengeluaran)
                if kategori == 'Bahan Pokok':
                    jumlah = random.randint(50, 300) * 1000  # 50k - 300k
                    deskripsi = f"Pembelian {random.choice(['Kopi', 'Susu', 'Gula', 'Tepung'])}"
                elif kategori == 'Barang':
                    jumlah = random.randint(100, 500) * 1000  # 100k - 500k
                    deskripsi = f"Pembelian {random.choice(['Peralatan', 'Kemasan', 'Perlengkapan'])}"
                elif kategori == 'Jasa':
                    jumlah = random.randint(50, 200) * 1000  # 50k - 200k
                    deskripsi = f"{random.choice(['Listrik', 'Air', 'Internet', 'Maintenance'])}"
                else:
                    jumlah = random.randint(20, 150) * 1000  # 20k - 150k
                    deskripsi = f"{random.choice(['Transport', 'ATK', 'Kebersihan', 'Lain-lain'])}"
            
            cursor.execute(
                'INSERT INTO transactions (tanggal, tipe, kategori, deskripsi, jumlah, user_id) VALUES (?, ?, ?, ?, ?, ?)',
                (date_str, tipe, kategori, deskripsi, jumlah, admin_id)
            )
            transaction_count += 1
    
    print(f"   ✓ Created {transaction_count} sample transactions")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("\n✅ Database initialization completed successfully!")
    print("\n📊 Sample Login Credentials:")
    print("=" * 50)
    print("Admin Account:")
    print("  Username: BagasNz")
    print("  Password: 162316")
    print("  Role: Full access to all features")
    print("-" * 50)
    print("Guest Accounts:")
    print("  Username: Refki | Password: owner")
    print("  Username: Iqbal | Password: owner")
    print("  Username: Rico  | Password: owner")
    print("  Username: Hari  | Password: owner")
    print("  Username: Dimse | Password: owner")
    print("  Role: Manage cashflow and view reports")
    print("=" * 50)
    print("\n🚀 You can now run the application with: python app.py")

if __name__ == '__main__':
    init_database()
