# 🎯 Panduan Login Cepat - Toko Kopi Makmur

## 🚀 Cara Menggunakan Login Credentials

### 1. **Mulai Aplikasi**

#### Option A: Local Development
```bash
python3 app.py
```

#### Option B: Docker (Recommended)
```bash
docker-compose up -d
```

#### Option C: Static Build (Netlify)
```bash
python3 static_build.py
# Upload folder 'dist' ke Netlify
```

### 2. **Akses Login Page**
- **URL**: `http://localhost:5000/login`
- ** atau** `https://your-deployed-app.com/login`

### 3. **Gunakan Credentials**

#### 👨‍💼 Login sebagai Admin
```
Username: BagasNz
Password: 162316
```
**Akses**: Dashboard admin lengkap dengan semua fitur

#### 👥 Login sebagai Guest
```
Username: [Pilih salah satu]
- Refki
- Iqbal  
- Rico
- Hari
- Dimse

Password: owner (sama untuk semua guest)
```
**Akses**: Fitur sesuai dengan role guest

## 📱 Fitur Setelah Login

### Dashboard Admin (BagasNz)
- ✅ View total revenue & expenses
- ✅ Manage transactions
- ✅ Generate financial reports
- ✅ User management
- ✅ Product management
- ✅ Cash flow analysis

### Dashboard Guest (Refki, Iqbal, Rico, Hari, Dimse)
- ✅ View financial dashboard (read-only)
- ✅ View transactions
- ✅ Generate reports (sesuai role)
- ❌ User management (admin only)
- ❌ Product management (admin only)

## 🛠 Quick Commands

```bash
# Test apakah credentials bekerja
python3 test_login_credentials.py

# Lihat status aplikasi
make status

# Check health
curl http://localhost:5000/health
```

## 🔍 Troubleshooting

### Jika Login Gagal:
1. **Pastikan aplikasi sudah running** (`python3 app.py` atau `docker-compose up -d`)
2. **Cek URL**: `http://localhost:5000/login`
3. **Cek credentials**: Pastikan username dan password benar
4. **Cek logs**: `make logs` (untuk Docker)

### Jika Database Error:
```bash
# Reset database
rm kopi_makmur.db
python3 init_db.py
```

## 📋 Summary

**✅ SEMUA CREDENTIALS SIAP:**
- **Admin**: BagasNz / 162316
- **Guest**: Refki, Iqbal, Rico, Hari, Dimse / owner

**✅ SIAP UNTUK SEMUA DEPLOYMENT:**
- Local development
- Docker container
- Netlify (static)
- Heroku
- Railway
- GitHub Pages

**✅ FITUR LENGKAP:**
- Role-based access
- Dashboard financial
- Transaction management
- Responsive design
- Mobile-friendly

---

**🚀 Aplikasi siap digunakan dengan login credentials di atas!**