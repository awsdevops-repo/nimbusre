#!/bin/bash

################################################################################
# NimbusRE Agent - SSL/TLS Setup Script (Let's Encrypt)
# Configures automatic SSL certificates with Certbot
################################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}NimbusRE Agent - SSL/TLS Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Get domain
DOMAIN="${1:-localhost}"

if [ "$DOMAIN" = "localhost" ] || [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}[!] SSL is only for public domains${NC}"
    echo "    For localhost development, HTTP is fine"
    echo "    Usage: sudo bash Deploy_Scripts/setup-ssl.sh your-domain.com"
    exit 0
fi

echo -e "${YELLOW}[*] Setting up SSL/TLS for: $DOMAIN${NC}\n"

################################################################################
# 1. VERIFY NGINX IS RUNNING
################################################################################
echo -e "${BLUE}[1/4] Verifying Nginx is running...${NC}"
if ! systemctl is-active --quiet nginx; then
    echo -e "${RED}✗ Nginx is not running${NC}"
    echo "    Run: sudo systemctl start nginx"
    exit 1
fi
echo -e "${GREEN}✓ Nginx is running${NC}"

################################################################################
# 2. VERIFY DOMAIN ACCESSIBILITY
################################################################################
echo -e "\n${BLUE}[2/4] Verifying domain DNS...${NC}"
if ping -c 1 "$DOMAIN" &> /dev/null; then
    echo -e "${GREEN}✓ Domain $DOMAIN is accessible${NC}"
else
    echo -e "${YELLOW}! Domain $DOMAIN may not be resolving${NC}"
    echo "    Make sure DNS is pointing to this server"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

################################################################################
# 3. CREATE CERTBOT DIRECTORIES
################################################################################
echo -e "\n${BLUE}[3/4] Creating certificate directories...${NC}"
mkdir -p /var/www/certbot
chown www-data:www-data /var/www/certbot
chmod 755 /var/www/certbot
echo -e "${GREEN}✓ Directories created${NC}"

################################################################################
# 4. REQUEST CERTIFICATE
################################################################################
echo -e "\n${BLUE}[4/4] Requesting Let's Encrypt certificate...${NC}"
echo "      Email: (will be used for certificate notifications)"
read -p "Enter your email address: " EMAIL

certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Certificate obtained successfully${NC}"
else
    echo -e "${RED}✗ Failed to obtain certificate${NC}"
    exit 1
fi

################################################################################
# 5. SETUP AUTO-RENEWAL
################################################################################
echo -e "\n${BLUE}[*] Setting up automatic certificate renewal...${NC}"

# Create renewal timer
cat > /etc/systemd/system/certbot-renew.service << EOF
[Unit]
Description=Renew Let's Encrypt Certificate
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew --quiet --agree-tos
ExecStartPost=/bin/systemctl reload nginx
StandardOutput=journal
StandardError=journal
EOF

cat > /etc/systemd/system/certbot-renew.timer << EOF
[Unit]
Description=Renew Let's Encrypt Certificate Daily
Requires=certbot-renew.service

[Timer]
OnCalendar=daily
OnBootSec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable certbot-renew.timer
systemctl start certbot-renew.timer

echo -e "${GREEN}✓ Auto-renewal configured (daily check)${NC}"

################################################################################
# 6. TEST SSL
################################################################################
echo -e "\n${BLUE}[*] Testing SSL certificate...${NC}"
sleep 2
systemctl reload nginx

if curl -I https://$DOMAIN &> /dev/null; then
    echo -e "${GREEN}✓ SSL certificate is working${NC}"
else
    echo -e "${YELLOW}! Could not verify SSL (check if site is accessible)${NC}"
fi

################################################################################
# SUMMARY
################################################################################
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}SSL/TLS Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}Certificate Details:${NC}"
echo "  Domain: $DOMAIN, www.$DOMAIN"
echo "  Issuer: Let's Encrypt"
echo "  Location: /etc/letsencrypt/live/$DOMAIN/"
echo "  Renewal: Automatic (daily check)"

echo -e "\n${BLUE}Useful Commands:${NC}"
echo "  View certificate: certbot certificates"
echo "  Renew now: sudo certbot renew --force-renewal"
echo "  View renewal status: sudo systemctl status certbot-renew.timer"
echo "  View renewal logs: sudo journalctl -u certbot-renew.service -f"

echo -e "\n${BLUE}Security Check:${NC}"
echo "  Run SSL Labs test: https://www.ssllabs.com/ssltest/?d=$DOMAIN"

echo -e "\n${BLUE}Accessing Application:${NC}"
echo "  https://$DOMAIN"
echo "  https://www.$DOMAIN"

echo -e "\n${BLUE}Certificate Expiration:${NC}"
certbot certificates 2>/dev/null | grep "Expiration Date" || echo "  Check: sudo certbot certificates"

echo -e "\n${GREEN}SSL setup successful!${NC}\n"
