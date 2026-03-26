#!/bin/bash
################################################################################
# NimbusRE Agent - Deployment Script (fixed)
# Run as root: sudo bash deploy.sh
################################################################################

set -euo pipefail
IFS=$'\n\t'

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

APP_DIR="/opt/nimbusre"
APP_USER="nimbusre"
FRONTEND_PORT="3000"
BACKEND_PORT="3001"

# Ensure running as root
if [[ $EUID -ne 0 ]]; then
  echo -e "${RED}This script must be run as root${NC}"
  echo "Please run: sudo bash deploy.sh"
  exit 1
fi

echo -e "${BLUE}NimbusRE Agent - Deployment (fixed)${NC}"

################################################################################
# 1. CREATE APP DIRECTORY
################################################################################
echo -e "${BLUE}[1/6] Setting up application directory...${NC}"
mkdir -p "$APP_DIR"
chown -R "${APP_USER}:${APP_USER}" "$APP_DIR"
chmod 750 "$APP_DIR"
echo -e "${GREEN}✓ Created $APP_DIR${NC}"

################################################################################
# 2. COPY APPLICATION FILES
################################################################################
echo -e "\n${BLUE}[2/6] Copying application files...${NC}"
# Require caller to run from repo root that contains frontend/ and src/
if [[ -d "$(pwd)/frontend" && -d "$(pwd)/src" ]]; then
  # copy as root then chown
  rsync -a --delete --omit-dir-times --no-perms ./ "$APP_DIR/"
  chown -R "${APP_USER}:${APP_USER}" "$APP_DIR"
  echo -e "${GREEN}✓ Application files copied to ${APP_DIR}${NC}"
else
  echo -e "${RED}✗ Please run this script from project root containing 'frontend' and 'src'${NC}"
  echo "  cd /path/to/project && sudo bash deploy.sh"
  exit 1
fi

################################################################################
# 3. INSTALL PYTHON BACKEND DEPENDENCIES (use venv, run as app user)
################################################################################
echo -e "\n${BLUE}[3/6] Installing Python backend dependencies...${NC}"

# Create venv owned by app user
runuser -l "$APP_USER" -c "python3 -m venv $APP_DIR/venv"
# Ensure permissions
chown -R "${APP_USER}:${APP_USER}" "$APP_DIR/venv"

# Install pip requirements via venv's pip (run as app user)
if [[ -f "$APP_DIR/requirements.txt" ]]; then
  runuser -l "$APP_USER" -c "PATH=$APP_DIR/venv/bin:\$PATH $APP_DIR/venv/bin/pip install --upgrade pip setuptools wheel && $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt"
  echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
  echo -e "${YELLOW}! requirements.txt not found at $APP_DIR/requirements.txt (skipping pip install)${NC}"
fi

################################################################################
# 4. INSTALL NODE FRONTEND DEPENDENCIES (run as app user)
################################################################################
echo -e "\n${BLUE}[4/6] Installing Node frontend dependencies...${NC}"

if [[ -d "$APP_DIR/frontend" ]]; then
  # Ensure frontend dir ownership
  chown -R "${APP_USER}:${APP_USER}" "$APP_DIR/frontend"
  # Install and build as app user using runuser
  runuser -l "$APP_USER" -c "cd $APP_DIR/frontend && npm install --unsafe-perm"
  # Build as app user
  runuser -l "$APP_USER" -c "cd $APP_DIR/frontend && npm run build"
  echo -e "${GREEN}✓ Frontend built successfully${NC}"
else
  echo -e "${YELLOW}! Frontend folder missing, skipping frontend build${NC}"
fi

################################################################################
# 5. CREATE SYSTEMD SERVICES
################################################################################
echo -e "\n${BLUE}[5/6] Creating systemd services...${NC}"

cat > /etc/systemd/system/nimbusre-backend.service <<'EOF'
[Unit]
Description=NimbusRE Agent Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=nimbusre
WorkingDirectory=/opt/nimbusre
Environment="PATH=/opt/nimbusre/venv/bin"
ExecStart=/opt/nimbusre/venv/bin/python -m uvicorn src.api.api_server:app --host 0.0.0.0 --port 3001 --workers 4
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/nimbusre-frontend.service <<'EOF'
[Unit]
Description=NimbusRE Agent Frontend (Next.js)
After=network.target

[Service]
Type=simple
User=nimbusre
WorkingDirectory=/opt/nimbusre/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/env node node_modules/.bin/next start -p 3000
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable nimbusre-backend.service || true
systemctl enable nimbusre-frontend.service || true

echo -e "${GREEN}✓ Systemd service files created${NC}"

################################################################################
# 6. ENV FILES + PERMS
################################################################################
echo -e "\n${BLUE}[6/6] Setting up environment files...${NC}"

cat > "$APP_DIR/.env" <<'EOF'
# Backend Configuration
ENVIRONMENT=production
DEBUG=false
PORT=3001
HOST=0.0.0.0
KUBECONFIG=/home/nimbusre/.kube/config
LOG_LEVEL=info
EOF

mkdir -p "$APP_DIR/frontend"
cat > "$APP_DIR/frontend/.env.local" <<'EOF'
NEXT_PUBLIC_BACKEND_URL=http://localhost:3001
NEXT_PUBLIC_ENABLE_ADVANCED_WORKFLOW=true
EOF

chown "$APP_USER:$APP_USER" "$APP_DIR/.env" "$APP_DIR/frontend/.env.local" || true
chmod 600 "$APP_DIR/.env" || true

echo -e "${GREEN}✓ Environment files created${NC}"

################################################################################
# START SERVICES
################################################################################
echo -e "\n${BLUE}[*] Starting services...${NC}"
systemctl restart nimbusre-backend || true
systemctl restart nimbusre-frontend || true
sleep 2

# Status checks
for svc in nimbusre-backend nimbusre-frontend; do
  if systemctl is-active --quiet "$svc"; then
    echo -e "${GREEN}✓ $svc is active${NC}"
  else
    echo -e "${RED}✗ $svc failed to start. Check: journalctl -u $svc -n 100${NC}"
  fi
done

echo -e "\n${GREEN}Deployment complete${NC}"

aws eks update-kubeconfig --name rd-eks-min-public --region eu-west-1

cp -f ~/.kube/config /opt/nimbusre/docker-desktop-config.yaml 