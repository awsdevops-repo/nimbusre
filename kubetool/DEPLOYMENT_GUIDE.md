# NimbusRE Agent - Ubuntu Deployment Guide

## Quick Start

Deploy the NimbusRE Agent application to Ubuntu in 4 easy steps:

```bash
# 1. Install system dependencies (run once)
sudo bash install.sh

# 2. Deploy application
sudo bash deploy.sh

# 3. Configure Nginx reverse proxy (optional, for domain/SSL)
sudo bash setup-nginx.sh [your-domain.com]

# 4. Set up SSL/TLS certificates (optional, requires domain)
sudo bash setup-ssl.sh your-domain.com
```

## Step-by-Step Installation

### Prerequisites
- Ubuntu 20.04 LTS or 22.04 LTS
- Root or sudo access
- Minimum 4GB RAM, 20GB storage
- Internet connection

### 1. Install Dependencies (`install.sh`)

This script installs:
- **Node.js 20.x LTS** - Frontend runtime
- **Python 3.11** - Backend runtime
- **Docker & Docker Compose** - Container platform
- **kubectl & Helm** - Kubernetes tools
- **Nginx** - Web server & reverse proxy
- **Certbot** - SSL/TLS certificate management
- **PM2** - Process manager for Node.js
- **ollama** Download model 

```bash
sudo bash install.sh
```

**Expected output:**
```
✓ Node.js version: v20.x.x
✓ npm version: 10.x.x
✓ Python version: Python 3.11.x
✓ Docker version: Docker 25.x.x
✓ kubectl version: v1.29.x
✓ Helm version: v3.x.x
✓ Nginx installed
✓ Certbot installed
✓ Ollama installed

```

### 2. Deploy Application (`deploy.sh`)

This script:
- Creates `/opt/nimbusre` application directory
- Installs Python dependencies
- Installs Node.js dependencies & builds frontend
- Creates systemd services for backend & frontend
- Configures environment files
- Starts services

```bash
sudo bash deploy.sh
```

**Expected output:**
```
✓ Backend service running on port 8000
✓ Frontend service running on port 3000
```

**Access the application:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 3. Configure Nginx (`setup-nginx.sh`)

Sets up Nginx as reverse proxy to serve through ports 80/443:

```bash
# For localhost (development)
sudo bash setup-nginx.sh

# For domain (production)
sudo bash setup-nginx.sh your-domain.com
```

**Access via:**
- `http://localhost` (development)
- `http://your-domain.com` (production)

### 4. Set up SSL (`setup-ssl.sh`)

Configures automatic SSL certificates with Let's Encrypt:

```bash
sudo bash setup-ssl.sh your-domain.com
```

**What happens:**
- Requests SSL certificate from Let's Encrypt
- Configures automatic renewal (daily)
- Updates Nginx configuration

**Access via:**
- `https://your-domain.com`
- `https://www.your-domain.com`

## Service Management

### Start/Stop Services

```bash
# Backend
sudo systemctl start nimbusre-backend
sudo systemctl stop nimbusre-backend
sudo systemctl restart nimbusre-backend

# Frontend
sudo systemctl start nimbusre-frontend
sudo systemctl stop nimbusre-frontend
sudo systemctl restart nimbusre-frontend

# Check status
sudo systemctl status nimbusre-backend
sudo systemctl status nimbusre-frontend
```

### View Logs

```bash
# Backend logs (live)
sudo journalctl -u nimbusre-backend -f

# Frontend logs (live)
sudo journalctl -u nimbusre-frontend -f

# Nginx error logs
sudo tail -f /var/log/nginx/nimbusre-error.log

# Nginx access logs
sudo tail -f /var/log/nginx/nimbusre-access.log
```

### Using Monitor Script

Interactive monitoring and maintenance:

```bash
sudo bash manage.sh
```

**Options:**
1. Check service status
2. View backend logs
3. View frontend logs
4. View error logs
5. Restart all services
6. Check system resources
7. Check API health
8. Clean logs
9. Database backup
10. View configuration

## Configuration Files

### Backend Configuration

Location: `/opt/nimbusre/.env`

```
ENVIRONMENT=production
DEBUG=false
PORT=8000
HOST=0.0.0.0
KUBECONFIG=/home/nimbusre/.kube/config
LOG_LEVEL=info
```

### Frontend Configuration

Location: `/opt/nimbusre/frontend/.env.local`

```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_ADVANCED_WORKFLOW=true
```

### Nginx Configuration

Location: `/etc/nginx/sites-available/nimbusre`

Routes:
- `/` → Frontend (port 3000)
- `/api/*` → Backend API (port 8000)
- `/docs` → API documentation
- `/health` → Health check endpoint

## Troubleshooting

### Backend not starting

```bash
# Check service status
sudo systemctl status nimbusre-backend

# View detailed logs
sudo journalctl -u nimbusre-backend -n 50

# Check port 8000 is available
sudo netstat -tlnp | grep 8000

# Manually test Python
cd /opt/nimbusre
source venv/bin/activate
python -m uvicorn src.api.api_server:app --host 0.0.0.0 --port 8000
```

### Frontend not starting

```bash
# Check service status
sudo systemctl status nimbusre-frontend

# View detailed logs
sudo journalctl -u nimbusre-frontend -n 50

# Check port 3000 is available
sudo netstat -tlnp | grep 3000

# Manually test Node.js
cd /opt/nimbusre/frontend
npm run build
npm start
```

### Nginx not responding

```bash
# Check Nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# View error logs
sudo tail -50 /var/log/nginx/nimbusre-error.log

# Restart Nginx
sudo systemctl restart nginx
```

### SSL Certificate Issues

```bash
# View certificate status
sudo certbot certificates

# View renewal logs
sudo journalctl -u certbot-renew.service -n 50

# Force renewal
sudo certbot renew --force-renewal

# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/your-domain/cert.pem -noout -dates
```

## System Resources

### Monitoring

Check resource usage:

```bash
# CPU & Memory
top -b -n 1 | head -20

# Disk space
df -h /opt/nimbusre

# Network connections
sudo netstat -tulnp | grep -E ':3000|:8000'

# Docker containers (if using)
docker ps
```

### Log Cleanup

```bash
# Clean systemd journal (keep 100MB)
sudo journalctl --vacuum=100M

# Rotate Nginx logs
sudo logrotate -f /etc/logrotate.d/nginx
```

## Backup & Restore

### Backup Configuration

```bash
# Run backup (using manage.sh)
sudo bash manage.sh
# Select option 9

# Or manually:
mkdir -p /opt/nimbusre/backups
tar -czf /opt/nimbusre/backups/nimbusre-$(date +%Y%m%d).tar.gz \
  -C /opt/nimbusre .env frontend/.env.local src/
```

### Restore from Backup

```bash
tar -xzf /opt/nimbusre/backups/nimbusre-backup.tar.gz -C /opt/nimbusre
sudo chown -R nimbusre:nimbusre /opt/nimbusre
sudo systemctl restart nimbusre-backend nimbusre-frontend
```

## Kubernetes Configuration

For Kubernetes access (monitoring/management):

```bash
# Create kubeconfig directory for nimbusre user
sudo mkdir -p /home/nimbusre/.kube
sudo chown nimbusre:nimbusre /home/nimbusre/.kube

# Copy your kubeconfig
sudo cp ~/.kube/config /home/nimbusre/.kube/
sudo chown nimbusre:nimbusre /home/nimbusre/.kube/config
sudo chmod 600 /home/nimbusre/.kube/config

# Test kubectl access
sudo -u nimbusre kubectl get pods -A
```

## Production Checklist

- [ ] System updated: `sudo apt update && apt upgrade`
- [ ] Dependencies installed: `sudo bash install.sh`
- [ ] Application deployed: `sudo bash deploy.sh`
- [ ] Nginx configured: `sudo bash setup-nginx.sh your-domain.com`
- [ ] SSL certificates set up: `sudo bash setup-ssl.sh your-domain.com`
- [ ] Firewall rules configured
- [ ] Backups scheduled
- [ ] Monitoring configured
- [ ] Log rotation enabled
- [ ] Health checks passing: `sudo bash manage.sh` → option 7
- [ ] Performance tested and optimized

## Performance Tuning

### Nginx Optimization

Edit `/etc/nginx/sites-available/nimbusre`:

```nginx
# Increase worker connections
worker_connections 2048;

# Enable gzip compression
gzip on;
gzip_types text/plain text/css application/json;
gzip_min_length 1000;

# Increase buffer sizes
proxy_buffer_size 128k;
proxy_buffers 4 256k;
proxy_busy_buffers_size 256k;
```

### Backend Optimization

Edit `/etc/systemd/system/nimbusre-backend.service`:

```ini
Environment="WORKERS=8"  # Increase for more CPU cores
ExecStart=/opt/nimbusre/venv/bin/python -m uvicorn \
  src.api.api_server:app --workers 8
```

### Frontend Optimization

Edit `/etc/systemd/system/nimbusre-frontend.service`:

```ini
Environment="NODE_OPTIONS=--max-old-space-size=2048"
```

## Support & Documentation

- **API Documentation**: `http://your-domain:8000/docs`
- **Project README**: `/opt/nimbusre/docs/README.md`
- **Deployment Guide**: `/opt/nimbusre/docs/DEPLOYMENT_CHECKLIST.md`
- **Architecture**: `/opt/nimbusre/docs/SETUP_AND_DEPLOYMENT.md`

## Security Recommendations

1. **Firewall Configuration**
   ```bash
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```

2. **User Permissions**
   ```bash
   # Run services as non-root user (already configured)
   sudo ls -l /opt/nimbusre
   # Should show: nimbusre:nimbusre
   ```

3. **Environment Secrets**
   - Store sensitive data in `.env` files
   - Restrict permissions: `chmod 600 /opt/nimbusre/.env`
   - Never commit `.env` to version control

4. **Regular Updates**
   ```bash
   # Check for updates weekly
   sudo apt update
   sudo apt list --upgradable
   
   # Apply security updates
   sudo apt upgrade
   ```

## Monitoring with Prometheus (Optional)

For advanced monitoring, install Prometheus:

```bash
sudo apt install -y prometheus grafana-server

# Configure targets in /etc/prometheus/prometheus.yml
# Add backend health endpoint: localhost:8000/metrics
```

## Getting Help

1. **Check logs first**: `sudo bash manage.sh` → option 4
2. **Verify services**: `sudo bash manage.sh` → option 1
3. **Test API**: `sudo bash manage.sh` → option 7
4. **Review configuration**: `sudo bash manage.sh` → option 10

---

**Created**: January 28, 2026
**Version**: 1.0
**Project**: NimbusRE Agent - Kubernetes Management Platform
