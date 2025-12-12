# Deployment Guide

## Overview
This guide covers deploying the Adaptive Intelligent Tutoring Framework to production environments.

## Pre-Deployment Checklist

- [ ] All tests passing (`pytest`)
- [ ] Code review completed
- [ ] Security audit performed
- [ ] Documentation updated
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] SSL certificates ready
- [ ] Backup strategy in place

## Deployment Architecture

```
┌─────────────────────────────────────┐
│      Client Browser / Frontend      │
└────────────┬────────────────────────┘
             │ HTTPS
             ↓
┌─────────────────────────────────────┐
│    Nginx (Reverse Proxy / Load      │
│    Balancer / SSL Termination)      │
└────────────┬────────────────────────┘
             │
    ┌────────┴─────────┐
    ↓                  ↓
┌─────────┐      ┌─────────┐
│Gunicorn │      │Gunicorn │
│ Worker1 │      │ Worker2 │
└────┬────┘      └────┬────┘
     │                 │
     └────────┬────────┘
              ↓
        ┌─────────────┐
        │ PostgreSQL  │
        │ Database    │
        └─────────────┘
```

## Option 1: Heroku Deployment

### Step 1: Prepare for Heroku

#### Create Procfile
```bash
# In project root
cat > Procfile << EOF
web: cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT main:app
EOF
```

#### Create runtime.txt
```bash
cat > runtime.txt << EOF
python-3.10.13
EOF
```

#### Update requirements.txt
```bash
cd backend
pip install gunicorn
pip freeze > requirements.txt
```

### Step 2: Deploy

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-postgres-url

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# Deploy
git push heroku main

# Run migrations
heroku run python backend/main.py

# Check logs
heroku logs --tail
```

## Option 2: Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: tutoring_db
      POSTGRES_USER: tutoring_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      DATABASE_URL: postgresql://tutoring_user:secure_password@db:5432/tutoring_db
      SECRET_KEY: your-secret-key
    depends_on:
      - db
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
```

### Step 3: Deploy with Docker

```bash
# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

## Option 3: Traditional VPS Deployment (Ubuntu/Nginx)

### Step 1: Server Setup

```bash
# SSH into server
ssh root@your_server_ip

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib nginx supervisor \
    certbot python3-certbot-nginx

# Create app user
useradd -m -s /bin/bash appuser
```

### Step 2: Deploy Application

```bash
# Switch to app user
su - appuser

# Clone repository
git clone <repository-url>
cd adaptive-tutoring-framework/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
cat > .env << EOF
FLASK_ENV=production
DATABASE_URL=postgresql://tutoring_user:password@localhost/tutoring_db
SECRET_KEY=your-very-secure-secret-key
EOF

chmod 600 .env
```

### Step 3: Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE tutoring_db;
CREATE USER tutoring_user WITH PASSWORD 'secure_password';
ALTER ROLE tutoring_user SET client_encoding TO 'utf8';
ALTER ROLE tutoring_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tutoring_user SET default_transaction_deferrable TO on;
ALTER ROLE tutoring_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE tutoring_db TO tutoring_user;
\q
```

### Step 4: Configure Gunicorn

```bash
# Create gunicorn config
cat > /home/appuser/adaptive-tutoring-framework/backend/gunicorn_config.py << EOF
import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 30
keepalive = 5
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
EOF
```

### Step 5: Configure Supervisor

```bash
# Create supervisor config
sudo cat > /etc/supervisor/conf.d/tutoring.conf << EOF
[program:tutoring-api]
directory=/home/appuser/adaptive-tutoring-framework/backend
command=/home/appuser/adaptive-tutoring-framework/backend/venv/bin/gunicorn -c gunicorn_config.py main:app
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/tutoring-api.log
environment=PATH="/home/appuser/adaptive-tutoring-framework/backend/venv/bin"
EOF

# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start tutoring-api
```

### Step 6: Configure Nginx

```bash
# Create Nginx config
sudo cat > /etc/nginx/sites-available/tutoring << 'EOF'
upstream tutoring {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    location / {
        proxy_pass http://tutoring;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /home/appuser/adaptive-tutoring-framework/frontend/;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/tutoring /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Configure SSL with Let's Encrypt

```bash
# Get SSL certificate
sudo certbot --nginx -d your_domain.com -d www.your_domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

### Step 8: Frontend Deployment

```bash
# Copy frontend files
sudo cp -r adaptive-tutoring-framework/frontend/* /var/www/html/

# Update API_BASE_URL in frontend/app.js
# Change from http://localhost:5000 to https://your_domain.com

# Set proper permissions
sudo chown -R www-data:www-data /var/www/html/
```

## Step 9: Database Initialization

```bash
# Create database tables
cd adaptive-tutoring-framework/backend
source venv/bin/activate
python main.py

# Load sample data (optional)
python scripts/seed_questions.py
```

## Step 10: Monitoring

### Application Logs
```bash
# Check API logs
tail -f /var/log/tutoring-api.log

# Check Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Check system logs
journalctl -u supervisor -f
```

### Health Check Endpoint
Add to `main.py`:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200
```

Test:
```bash
curl https://your_domain.com/health
```

## Configuration Management

### Production Environment Variables
```bash
# Create .env file
FLASK_ENV=production
DEBUG=False
SECRET_KEY=very-secure-random-key
DATABASE_URL=postgresql://user:password@host:5432/dbname
ALLOWED_HOSTS=your_domain.com,www.your_domain.com
CORS_ORIGINS=https://your_domain.com,https://www.your_domain.com
LOG_LEVEL=INFO
```

### Database Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/tutoring"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump tutoring_db | gzip > $BACKUP_DIR/tutoring_db_$DATE.sql.gz

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

Schedule with crontab:
```bash
0 2 * * * /path/to/backup_script.sh
```

## Performance Optimization

### Database Indexing
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_student_email ON student(email);
CREATE INDEX idx_session_student_id ON session(student_id);
CREATE INDEX idx_session_status ON session(status);
CREATE INDEX idx_engagement_session_id ON engagement_metric(session_id);
CREATE INDEX idx_adaptation_session_id ON adaptation_log(session_id);
```

### Caching
```python
# Add Redis caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/analytics/dashboard/<student_id>')
@cache.cached(timeout=300)  # Cache for 5 minutes
def dashboard(student_id):
    # Implementation
```

### Content Delivery
```nginx
# Add to Nginx config
gzip on;
gzip_min_length 1000;
gzip_types text/plain text/css text/xml text/javascript 
           application/x-javascript application/xml+rss 
           application/json;

expires 1h;
add_header Cache-Control "public, max-age=3600";
```

## Security Hardening

### HTTPS Enforcement
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your_domain.com;
    return 301 https://$server_name$request_uri;
}
```

### Security Headers
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Database Security
```bash
# Restrict database user privileges
# Only allow specific operations needed

# Use strong passwords
# Minimum 16 characters with mixed case, numbers, symbols

# Enable SSL for database connections
postgresql: ssl=require in connection string
```

### Application Security
```python
# Flask security configurations
app.config['SESSION_COOKIE_SECURE'] = True      # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True    # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Rate limiting
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)
@app.route('/api/endpoint')
@limiter.limit("100/hour")
def endpoint():
    pass
```

## Monitoring & Alerting

### Application Monitoring
```bash
# Install monitoring tools
apt-get install -y prometheus grafana-server

# Monitor metrics:
# - CPU usage
# - Memory usage
# - Request response time
# - Error rates
# - Database connection pool
```

### Log Aggregation
```bash
# Install ELK stack or use cloud service
# Elasticsearch for log storage
# Kibana for visualization
# Logstash for log processing
```

### Alerts
Configure alerts for:
- High error rates (>5%)
- Slow response times (>2s average)
- Database connection failures
- Disk space (>90% full)
- Memory usage (>85%)

## Maintenance & Updates

### Regular Tasks

**Daily**:
- Monitor error logs
- Check system resources
- Verify health check endpoint

**Weekly**:
- Review analytics data
- Check database size growth
- Backup verification

**Monthly**:
- Security updates
- Dependency updates
- Performance review
- Capacity planning

### Update Procedure

```bash
# 1. Backup database and files
pg_dump tutoring_db > backup_$(date +%Y%m%d).sql
tar -czf backend_backup_$(date +%Y%m%d).tar.gz backend/

# 2. Stop application
sudo supervisorctl stop tutoring-api

# 3. Update code
git pull origin main

# 4. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Run migrations
python main.py

# 6. Test changes
pytest

# 7. Restart application
sudo supervisorctl start tutoring-api

# 8. Verify deployment
curl https://your_domain.com/health
```

## Troubleshooting Production

### Application Not Starting
```bash
# Check supervisor status
sudo supervisorctl status

# Check logs
sudo tail -100 /var/log/tutoring-api.log

# Check Python errors
sudo supervisorctl restart tutoring-api
```

### Database Connection Issues
```bash
# Test database connection
psql -h localhost -U tutoring_user -d tutoring_db

# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### High CPU/Memory Usage
```bash
# Monitor processes
top -u appuser

# Check Gunicorn workers
ps aux | grep gunicorn

# Adjust worker count in gunicorn config
# workers = multiprocessing.cpu_count() * 2 + 1
```

## Rollback Procedure

If deployment fails:
```bash
# 1. Restore from backup
git revert <commit-hash>

# 2. Restore database
psql tutoring_db < backup_YYYYMMDD.sql

# 3. Restart application
sudo supervisorctl restart tutoring-api

# 4. Verify
curl https://your_domain.com/health
```

## Scaling Considerations

As user base grows:

### Horizontal Scaling
- Add more Gunicorn workers
- Use load balancer (Nginx, HAProxy)
- Multiple application servers

### Vertical Scaling
- Increase server CPU/memory
- Upgrade database instance
- Add caching layer (Redis)

### Database Scaling
- Read replicas for analytics queries
- Connection pooling (PgBouncer)
- Partitioning for large tables

## Post-Deployment

1. **Verify Deployment**
   - Check all endpoints working
   - Verify SSL certificate
   - Test from different browsers

2. **Monitor First 24 Hours**
   - Watch error logs closely
   - Monitor performance metrics
   - Check database performance

3. **Collect Feedback**
   - User testing
   - Performance baseline
   - Security review

## Support

For deployment issues:
- Check logs in `/var/log/`
- Review supervisor status
- Test individual components
- Consult framework documentation

---

**Production Deployment Complete!** 🚀

For questions or issues, refer to the development guide or contact the team.
