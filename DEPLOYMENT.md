# Toko Kopi Makmur - Production Deployment Guide

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy with Docker Compose
./deploy.sh docker
```

### Option 2: Manual Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Run application
python app.py
```

## 🐳 Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### Commands

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Docker Services
- **kopi-makmur-app**: Main Flask application
- **nginx**: Reverse proxy (optional)

## ☁️ Cloud Deployment Platforms

### 1. Netlify Deployment

#### Prerequisites
- Netlify account
- Netlify CLI: `npm install -g netlify-cli`
- GitHub repository

#### Steps
1. **Connect GitHub to Netlify**
   - Go to [Netlify](https://netlify.com)
   - Click "New site from Git"
   - Connect your GitHub repository

2. **Set Environment Variables**
   - Go to Site Settings > Environment variables
   - Add:
     - `FLASK_ENV=production`
     - `SECRET_KEY=your-secret-key`
     - `PORT=5000`

3. **Configure Build Settings**
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `.` (or empty)
   - Functions directory: `netlify/functions`

4. **Deploy**
   ```bash
   # Using CLI
   export NETLIFY_AUTH_TOKEN=your-token
   export NETLIFY_SITE_ID=your-site-id
   ./deploy.sh netlify
   ```

### 2. Heroku Deployment

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Steps
1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DATABASE_URL=postgresql://...
   ```

3. **Deploy**
   ```bash
   # Using Heroku Git
   git push heroku main

   # Or using deploy script
   export HEROKU_API_KEY=your-api-key
   export HEROKU_APP_NAME=your-app-name
   ./deploy.sh heroku
   ```

### 3. Railway Deployment

#### Prerequisites
- Railway account
- Railway CLI: `npm install -g @railway/cli`

#### Steps
1. **Create Railway Project**
   ```bash
   railway login
   railway init
   ```

2. **Set Environment Variables**
   ```bash
   railway variables set FLASK_ENV=production
   railway variables set SECRET_KEY=your-secret-key
   ```

3. **Deploy**
   ```bash
   # Using CLI
   export RAILWAY_TOKEN=your-token
   ./deploy.sh railway

   # Or using Git
   git push origin main
   ```

### 4. Render Deployment

#### Prerequisites
- Render account
- GitHub repository

#### Steps
1. **Create Web Service**
   - Go to [Render](https://render.com)
   - Click "New" > "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - Add environment variables in the dashboard

### 5. GitHub Pages (Static Build)

For static version deployment:

```bash
# Build static version
python static_build.py

# Push to gh-pages branch
git checkout -b gh-pages
git add dist/
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

## 🗄️ Database Configuration

### SQLite (Default - Development)
```env
DATABASE_URL=sqlite:///kopi_makmur.db
```

### PostgreSQL (Recommended for Production)
```env
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### MySQL
```env
DATABASE_URL=mysql://username:password@host:port/database_name
```

### Cloud Databases
- **Heroku Postgres**: Automatically set by Heroku
- **Railway**: Use Railway PostgreSQL add-on
- **MongoDB Atlas**: Use MongoDB connection string

## 🔧 Environment Configuration

### Required Environment Variables

```env
# Core Flask
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
PORT=5000

# Database
DATABASE_URL=sqlite:///kopi_makmur.db

# Optional: Redis for sessions
REDIS_URL=redis://localhost:6379/0
```

### Security Notes
- Change `SECRET_KEY` in production
- Use strong passwords for database
- Enable HTTPS in production
- Set proper CORS headers

## 📊 Monitoring & Health Checks

### Health Check Endpoint
- URL: `https://your-app.com/health`
- Returns JSON status

### Monitoring Setup

#### LogRocket Integration
```html
<!-- Add to layout.html -->
<script src="https://cdn.logrocket.com/LogRocket.min.js"></script>
<script>LogRocket.init('your-app-id');</script>
```

#### Sentry Error Tracking
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

## 🔄 CI/CD with GitHub Actions

### Automated Deployment
1. **Enable GitHub Actions**
   - Add secrets to repository settings:
     - `NETLIFY_AUTH_TOKEN`
     - `NETLIFY_SITE_ID`
     - `HEROKU_API_KEY`
     - `HEROKU_APP_NAME`
     - `RAILWAY_TOKEN`

2. **Push to Main Branch**
   ```bash
   git push origin main
   ```

3. **Monitor Deployment**
   - Check Actions tab in GitHub
   - Monitor deployment logs

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

#### Database Connection Issues
```bash
# Check database file permissions
ls -la kopi_makmur.db

# Reset database
rm kopi_makmur.db
python init_db.py
```

#### Docker Build Failures
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### Performance Optimization

#### Database Indexes
```sql
-- Add indexes for better performance
CREATE INDEX idx_transactions_date ON transactions(tanggal);
CREATE INDEX idx_transactions_type ON transactions(tipe);
CREATE INDEX idx_products_category ON products(kategoria);
```

#### Caching
```python
from flask_caching import Cache

app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = os.getenv('REDIS_URL')

cache = Cache(app)

@app.route('/api/dashboard-stats')
@cache.cached(timeout=300)  # Cache for 5 minutes
def api_dashboard_stats():
    # Your code here
    pass
```

## 📱 Mobile Responsive

The application is already optimized for mobile with:
- Bootstrap 5 responsive design
- Touch-friendly interface
- Mobile-first CSS approach

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Set proper database permissions
- [ ] Enable rate limiting
- [ ] Add input validation
- [ ] Implement CSRF protection
- [ ] Use environment variables for secrets
- [ ] Regular security updates

## 📈 Scaling

### Horizontal Scaling
- Use load balancer (nginx/HAProxy)
- Multiple app instances with gunicorn
- Database connection pooling

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Add Redis for session storage

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Test locally with Docker
4. Check platform-specific documentation
5. Create an issue in the repository

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] Database migrated and seeded
- [ ] SSL/HTTPS enabled
- [ ] Security headers configured
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Load testing completed
- [ ] Error tracking configured
- [ ] Performance monitoring enabled
- [ ] Documentation updated