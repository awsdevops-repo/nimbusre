#!/bin/bash

################################################################################
# NimbusRE Agent - Deployment Script
# Deploys frontend and backend to Ubuntu server
################################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}NimbusRE Agent - Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Configuration
APP_DIR="/opt/nimbusre"
APP_USER="nimbusre"
FRONTEND_PORT="3000"
BACKEND_PORT="8000"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
    echo "Please run: sudo bash Deploy_Scripts/deploy.sh"
   exit 1
fi

################################################################################
# 1. CREATE APP DIRECTORY
################################################################################
echo -e "${BLUE}[1/6] Setting up application directory...${NC}"
mkdir -p $APP_DIR
chown -R $APP_USER:$APP_USER $APP_DIR
echo -e "${GREEN}✓ Created $APP_DIR${NC}"

################################################################################
# 2. CLONE/COPY APPLICATION
################################################################################
echo -e "\n${BLUE}[2/6] Copying application files...${NC}"

# If running from the source directory, copy files
if [ -d "$(pwd)/frontend" ] && [ -d "$(pwd)/src" ]; then
    cp -r . $APP_DIR/
    echo -e "${GREEN}✓ Application files copied${NC}"
else
    echo -e "${YELLOW}! Please run this script from the kubetool root directory${NC}"
    echo "  cd /path/to/kubetool && sudo bash Deploy_Scripts/deploy.sh"
    exit 1
fi

cd $APP_DIR
chown -R $APP_USER:$APP_USER $APP_DIR

################################################################################
# 3. INSTALL PYTHON BACKEND DEPENDENCIES
################################################################################
echo -e "\n${BLUE}[3/6] Installing Python backend dependencies...${NC}"

# Create virtual environment
sudo -u $APP_USER python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

echo -e "${GREEN}✓ Python dependencies installed${NC}"

################################################################################
# 4. INSTALL NODE.JS FRONTEND DEPENDENCIES
################################################################################
echo -e "\n${BLUE}[4/6] Installing Node.js frontend dependencies...${NC}"

cd $APP_DIR/frontend
sudo -u $APP_USER npm install
npm run build

echo -e "${GREEN}✓ Frontend built successfully${NC}"

cd $APP_DIR

################################################################################
# 5. CREATE SYSTEMD SERVICES
################################################################################
echo -e "\n${BLUE}[5/6] Creating systemd services...${NC}"

# Backend service
cat > /etc/systemd/system/nimbusre-backend.service << 'EOF'
[Unit]
Description=NimbusRE Agent Backend (FastAPI)
After=network.target

[Service]
Type=notify
User=nimbusre
WorkingDirectory=/opt/nimbusre
Environment="PATH=/opt/nimbusre/venv/bin"
ExecStart=/opt/nimbusre/venv/bin/python -m uvicorn src.api.api_server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
cat > /etc/systemd/system/nimbusre-frontend.service << 'EOF'
[Unit]
Description=NimbusRE Agent Frontend (Next.js)
After=network.target

[Service]
Type=simple
User=nimbusre
WorkingDirectory=/opt/nimbusre/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/node node_modules/.bin/next start -p 3000
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable nimbusre-backend.service
systemctl enable nimbusre-frontend.service

echo -e "${GREEN}✓ Systemd services created${NC}"

################################################################################
# 6. CREATE ENVIRONMENT FILES
################################################################################
echo -e "\n${BLUE}[6/6] Setting up environment configuration...${NC}"

# Backend .env
cat > $APP_DIR/.env << 'EOF'
# Backend Configuration
ENVIRONMENT=production
DEBUG=false
PORT=8000
HOST=0.0.0.0

# Kubernetes
KUBECONFIG=/home/nimbusre/.kube/config

# Logging
LOG_LEVEL=info
EOF

# Frontend .env.local
cat > $APP_DIR/frontend/.env.local << 'EOF'
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_ADVANCED_WORKFLOW=true
EOF

chown $APP_USER:$APP_USER $APP_DIR/.env
chown $APP_USER:$APP_USER $APP_DIR/frontend/.env.local
chmod 600 $APP_DIR/.env

echo -e "${GREEN}✓ Environment files created${NC}"

################################################################################
# START SERVICES
################################################################################
echo -e "\n${BLUE}[*] Starting services...${NC}"

systemctl start nimbusre-backend
systemctl start nimbusre-frontend

sleep 2

# Check status
if systemctl is-active --quiet nimbusre-backend; then
    echo -e "${GREEN}✓ Backend service running on port $BACKEND_PORT${NC}"
else
    echo -e "${RED}✗ Backend service failed to start${NC}"
    systemctl status nimbusre-backend
fi

if systemctl is-active --quiet nimbusre-frontend; then
    echo -e "${GREEN}✓ Frontend service running on port $FRONTEND_PORT${NC}"
else
    echo -e "${RED}✗ Frontend service failed to start${NC}"
    systemctl status nimbusre-frontend
fi

################################################################################
# SUMMARY
################################################################################
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}Application Paths:${NC}"
echo "  Application Root: $APP_DIR"
echo "  Frontend: $APP_DIR/frontend"
echo "  Backend: $APP_DIR/src"

echo -e "\n${BLUE}Service Management:${NC}"
echo "  Start Backend:   sudo systemctl start nimbusre-backend"
echo "  Stop Backend:    sudo systemctl stop nimbusre-backend"
echo "  Status Backend:  sudo systemctl status nimbusre-backend"
echo "  View Backend Logs: sudo journalctl -u nimbusre-backend -f"
echo ""
echo "  Start Frontend:  sudo systemctl start nimbusre-frontend"
echo "  Stop Frontend:   sudo systemctl stop nimbusre-frontend"
echo "  Status Frontend: sudo systemctl status nimbusre-frontend"
echo "  View Frontend Logs: sudo journalctl -u nimbusre-frontend -f"

echo -e "\n${BLUE}Access Application:${NC}"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"

echo -e "\n${BLUE}Next Steps:${NC}"
echo "  1. Configure Nginx: sudo bash $APP_DIR/Deploy_Scripts/setup-nginx.sh"
echo "  2. Set up SSL: sudo bash $APP_DIR/Deploy_Scripts/setup-ssl.sh <your-domain>"
echo "  3. Configure Kubernetes access for $APP_USER user"
echo "  4. Monitor logs: sudo journalctl -u nimbusre-backend -f"

echo -e "\n${GREEN}Deployment successful!${NC}\n"
