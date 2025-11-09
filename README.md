# 🏪 Toko Kopi Makmur - Sistem Manajemen Toko

Aplikasi web untuk mengelola cashflow, produk, dan user untuk Toko Kopi Makmur.

## ✨ Fitur Utama

### 🔐 Multi-Role Authentication
- **Admin**: Akses penuh ke semua fitur
- **User**: Kelola cashflow dan lihat laporan
- **View Only**: Hanya melihat dashboard (read-only)

### 💰 Manajemen Cashflow
- Tambah, edit, hapus transaksi pendapatan & pengeluaran
- Filter berdasarkan tanggal, bulan, tahun
- Kategori pengeluaran: Bahan Pokok, Barang, Jasa, Lain-lain

### 📊 Dashboard & Laporan
- Statistik real-time (pendapatan, pengeluaran, laba)
- Grafik interaktif dengan Chart.js
- Trend bulanan dan kategori pengeluaran
- Export laporan (PDF, Excel) - coming soon

### 📦 Manajemen Produk
- CRUD produk (nama, kategori, harga, stok)
- Status stok (Tersedia, Rendah, Habis)
- Kategori: Kopi, Minuman, Makanan, Snack

### 👥 Manajemen User (Admin Only)
- Tambah, edit, hapus user
- Assign role: admin, user, viewonly

## 🚀 Cara Menjalankan

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Inisialisasi Database
```bash
python init_db.py
```

Ini akan membuat database `kopi_makmur.db` dengan data sample:
- 3 user (admin, user1, viewer)
- Sample produk kopi & makanan
- 90 hari transaksi sample

### 3️⃣ Jalankan Aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di: **http://localhost:5000**

## 🔑 Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Akses**: Full control semua fitur

### User Account
- **Username**: `user1`
- **Password**: `user123`
- **Akses**: Cashflow & laporan

### View Only Account
- **Username**: `viewer`
- **Password**: `view123`
- **Akses**: Dashboard read-only

## 📁 Struktur Aplikasi

```
/workspace/
├── app.py                      # Flask application & routes
├── schema.sql                  # Database schema
├── init_db.py                  # Database initialization script
├── requirements.txt            # Python dependencies
├── kopi_makmur.db             # SQLite database (auto-created)
├── templates/                  # HTML templates
│   ├── layout.html            # Base template
│   ├── login.html             # Login page
│   ├── admin_dashboard.html   # Admin dashboard
│   ├── cashflow_index.html    # Cashflow management
│   ├── manajemen_user.html    # User management
│   ├── manajemen_product.html # Product management
│   ├── edit_transaksi.html    # Edit transaction form
│   ├── laporan_cashflow.html  # Reports & charts
│   ├── viewonly.html          # Read-only dashboard
│   ├── 404.html               # Not found page
│   └── 500.html               # Server error page
└── static/
    └── logo1.jpg              # Logo Toko Kopi Makmur
```

## 🎨 Teknologi

- **Backend**: Flask 3.0 (Python)
- **Database**: SQLite3
- **Frontend**: Bootstrap 5.3.2
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js
- **Template Engine**: Jinja2

## 🎨 Design System

- **Primary Color**: Green (#2c4f42, #3a6657)
- **Accent Color**: Gold (#d4af37)
- **Modern UI**: Gradient backgrounds, rounded corners, shadows
- **Responsive**: Mobile-friendly design

## 📝 Database Schema

### Users Table
- id, username, password (hashed), role, created_at

### Transactions Table
- id, tanggal, tipe (pendapatan/pengeluaran), kategori, deskripsi, jumlah, user_id, created_at

### Products Table
- id, nama, kategori, harga, stok, created_at

## ⚠️ Catatan Keamanan

**PENTING**: Untuk production:
1. Ganti `app.secret_key` di `app.py`
2. Gunakan password yang lebih kuat
3. Aktifkan HTTPS
4. Gunakan database yang lebih robust (PostgreSQL/MySQL)
5. Tambahkan rate limiting untuk login

## 🔄 Update & Maintenance

### Reset Database
Jika ingin reset database dengan data baru:
```bash
rm kopi_makmur.db
python init_db.py
```

### Backup Database
```bash
cp kopi_makmur.db kopi_makmur_backup_$(date +%Y%m%d).db
```

## 📧 Support

Untuk pertanyaan atau bantuan, hubungi administrator sistem.

---

**© 2025 Toko Kopi Makmur. All rights reserved.**
