# 🚀 Quick Start Guide - Toko Kopi Makmur

## ⚡ Super Cepat! (3 Langkah)

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Setup Database
```bash
python init_db.py
```

### 3️⃣ Run Application
```bash
python app.py
```

**DONE!** Buka browser: **http://localhost:5000**

---

## 🔐 Login

| Role | Username | Password | Akses |
|------|----------|----------|-------|
| **Admin** | `admin` | `admin123` | ✅ Full access semua fitur |
| **User** | `user1` | `user123` | 📊 Cashflow & laporan |
| **Viewer** | `viewer` | `view123` | 👁️ Dashboard only (read) |

---

## 📱 Fitur yang Tersedia

### 👨‍💼 Admin
- ✅ Dashboard dengan grafik real-time
- ✅ Manajemen Cashflow (CRUD)
- ✅ Manajemen Produk (CRUD)
- ✅ Manajemen User (CRUD)
- ✅ Laporan & Export

### 👤 User
- ✅ Manajemen Cashflow
- ✅ Lihat Laporan
- ❌ Tidak bisa kelola user/produk

### 👁️ View Only
- ✅ Lihat Dashboard
- ❌ Tidak bisa edit apapun

---

## 🎯 Halaman Utama

| URL | Halaman | Role |
|-----|---------|------|
| `/` | Login Page | All |
| `/admin/dashboard` | Admin Dashboard | Admin |
| `/cashflow` | Cashflow Management | Admin, User |
| `/products` | Product Management | Admin |
| `/users` | User Management | Admin |
| `/laporan` | Reports & Charts | Admin, User |
| `/viewonly` | Read-only Dashboard | View Only |

---

## 💾 Database

**File**: `kopi_makmur.db` (SQLite)

### Tables
1. **users** - User accounts & roles
2. **transactions** - Cashflow data
3. **products** - Product inventory

### Sample Data
- ✅ 3 users (admin, user1, viewer)
- ✅ 9 produk kopi & makanan
- ✅ 321 transaksi sample (90 hari terakhir)

---

## 🔄 Reset Database

Jika ingin reset ulang dengan data baru:

```bash
rm kopi_makmur.db
python init_db.py
```

---

## 🛠️ Troubleshooting

### Error: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Error: Database not found
```bash
python init_db.py
```

### Port 5000 sudah digunakan
Edit `app.py` line terakhir:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Ganti 5000 ke 8080
```

---

## 📊 Sample Transactions

Database sudah terisi dengan:
- 💰 **Pendapatan**: Penjualan kopi, makanan, minuman
- 💸 **Pengeluaran**: Bahan pokok, barang, jasa, dll
- 📈 **Period**: 90 hari terakhir
- 📉 **Grafik**: Ready untuk analisis

---

## 🎨 Customize

### Ganti Logo
Replace file: `static/logo1.jpg`

### Ubah Warna
Edit di `templates/layout.html`:
```css
--primary-green: #2c4f42;  /* Warna utama */
--gold: #d4af37;           /* Warna aksen */
```

### Ubah Nama Toko
Search & replace "Toko Kopi Makmur" di semua file templates

---

## ⚠️ Production Checklist

Sebelum deploy ke production:

- [ ] Ganti `app.secret_key` di `app.py`
- [ ] Gunakan password yang kuat
- [ ] Aktifkan HTTPS
- [ ] Gunakan production WSGI server (gunicorn/uwsgi)
- [ ] Pindah ke PostgreSQL/MySQL untuk database
- [ ] Setup backup otomatis database
- [ ] Tambah rate limiting untuk security

---

## 📞 Need Help?

1. Baca `README.md` untuk detail lengkap
2. Check file `app.py` untuk logic routes
3. Check `schema.sql` untuk struktur database
4. Check `templates/` untuk UI components

---

**Selamat mencoba! 🎉**

*Toko Kopi Makmur © 2025*
