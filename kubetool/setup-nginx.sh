#!/bin/bash

################################################################################
# NimbusRE Agent - Nginx Configuration Script
# Sets up Nginx as reverse proxy for frontend and backend
################################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}NimbusRE Agent - Nginx Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Configuration
DOMAIN="${1:-localhost}"
APP_DIR="/opt/nimbusre"

echo -e "${YELLOW}[*] Configuring Nginx for domain: $DOMAIN${NC}\n"

################################################################################
# BACKUP EXISTING CONFIG
################################################################################
echo -e "${BLUE}[1/4] Backing up existing Nginx configuration...${NC}"
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%s)
echo -e "${GREEN}✓ Backup created${NC}"

################################################################################
# CREATE UPSTREAM DEFINITIONS
################################################################################
echo -e "\n${BLUE}[2/4] Creating upstream server definitions...${NC}"

cat > /etc/nginx/conf.d/nimbusre-upstream.conf << 'EOF'
upstream nimbusre_frontend {
    least_conn;
    server 127.0.0.1:3000 max_fails=3 fail_timeout=30s;
}

upstream nimbusre_backend {
    least_conn;
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}
EOF

echo -e "${GREEN}✓ Upstream definitions created${NC}"

################################################################################
# CREATE VIRTUAL HOST CONFIG
################################################################################
echo -e "\n${BLUE}[3/4] Creating virtual host configuration...${NC}"

if [ "$DOMAIN" = "localhost" ]; then
    # HTTP only for localhost
    cat > /etc/nginx/sites-available/nimbusre << EOF
server {
    listen 80;
    listen [::]:80;
    server_name localhost 127.0.0.1;

    # Logging
    access_log /var/log/nginx/nimbusre-access.log combined;
    error_log /var/log/nginx/nimbusre-error.log warn;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Proxy timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Frontend
    location / {
        proxy_pass http://nimbusre_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://nimbusre_backend/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend docs
    location /docs {
        proxy_pass http://nimbusre_backend/docs;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
else
    # HTTP with redirect to HTTPS for domain
    cat > /etc/nginx/sites-available/nimbusre << EOF
# HTTP redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL certificates (certbot will update these)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Logging
    access_log /var/log/nginx/nimbusre-access.log combined;
    error_log /var/log/nginx/nimbusre-error.log warn;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Proxy timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Frontend
    location / {
        proxy_pass http://nimbusre_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://nimbusre_backend/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend docs
    location /docs {
        proxy_pass http://nimbusre_backend/docs;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
fi

echo -e "${GREEN}✓ Virtual host configuration created${NC}"

################################################################################
# ENABLE SITE
################################################################################
echo -e "\n${BLUE}[4/4] Enabling site and testing configuration...${NC}"

# Enable site
ln -sf /etc/nginx/sites-available/nimbusre /etc/nginx/sites-enabled/nimbusre

# Disable default site
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
if nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}✗ Nginx configuration has errors${NC}"
    exit 1
fi

# Reload Nginx
systemctl reload nginx

echo -e "${GREEN}✓ Nginx reloaded${NC}"

################################################################################
# SUMMARY
################################################################################
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Nginx Configuration Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}Configuration:${NC}"
echo "  Domain: $DOMAIN"
echo "  Frontend upstream: 127.0.0.1:3000"
echo "  Backend upstream: 127.0.0.1:8000"

echo -e "\n${BLUE}Nginx files:${NC}"
echo "  Upstream config: /etc/nginx/conf.d/nimbusre-upstream.conf"
echo "  Virtual host: /etc/nginx/sites-available/nimbusre"
echo "  Error logs: /var/log/nginx/nimbusre-error.log"
echo "  Access logs: /var/log/nginx/nimbusre-access.log"

echo -e "\n${BLUE}Service commands:${NC}"
echo "  Reload config: sudo systemctl reload nginx"
echo "  Restart Nginx: sudo systemctl restart nginx"
echo "  View logs: sudo tail -f /var/log/nginx/nimbusre-error.log"

if [ "$DOMAIN" != "localhost" ]; then
    echo -e "\n${BLUE}Next Step - Set up SSL/TLS:${NC}"
    echo "  Run: sudo bash /opt/nimbusre/setup-ssl.sh $DOMAIN"
fi

echo -e "\n${BLUE}Access Application:${NC}"
if [ "$DOMAIN" = "localhost" ]; then
    echo "  http://localhost"
else
    echo "  https://$DOMAIN"
    echo "  https://www.$DOMAIN"
fi

echo -e "\n${GREEN}Configuration successful!${NC}\n"
