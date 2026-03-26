#!/bin/bash
################################################################################
# NimbusRE Agent - Ubuntu Installation Script (AWS Ubuntu-friendly, noninteractive)
# - Prevents interactive prompts and service restart popups
# - Reinstalls python3-apt to avoid cnf-update-db errors
# - Ensures services are explicitly restarted at the end
################################################################################

set -euo pipefail
IFS=$'\n\t'

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}NimbusRE Agent - Installation Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Must run as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   echo "Please run: sudo bash install.sh"
   exit 1
fi

# Ensure noninteractive debconf/apt
export DEBIAN_FRONTEND=noninteractive
export DEBCONF_NONINTERACTIVE_SEEN=true

# dpkg options: accept defaults for config file prompts
DPKG_OPTS=( -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" )

# Temporary policy-rc.d to block automatic start/restart of services during package operations
POLICY_RC_D=/usr/sbin/policy-rc.d
cleanup() {
  # remove temporary policy if present
  if [[ -f "${POLICY_RC_D}" ]]; then
    echo "Removing temporary ${POLICY_RC_D}"
    rm -f "${POLICY_RC_D}" || true
    echo -e "${YELLOW}Removed temporary policy-rc.d${NC}"
  fi
  
  
}
cleanup

cat > "${POLICY_RC_D}" <<'EOF'
#!/bin/sh
# Prevent init/systemd service restarts during package installs (exit 101)
# Temporary stub created by NimbusRE installer.
echo "Package install blocking service restart (policy-rc.d stub)"
exit 101
EOF
chmod +x "${POLICY_RC_D}"
echo -e "${YELLOW}Temporary policy-rc.d created to prevent service restarts during install${NC}"

# Detect Ubuntu version
OS_VERSION=$(lsb_release -rs || echo "unknown")
echo -e "${YELLOW}[*] Detected Ubuntu ${OS_VERSION}${NC}"

################################################################################
# Pre-fix common apt hook failure (cnf-update-db / apt_pkg) by ensuring python3-apt
################################################################################
echo -e "\n${BLUE}[0/8] Ensure python3-apt to avoid cnf-update-db failures${NC}"
# Use apt-get and tolerate failure of reinstall once; we'll continue but keep noninteractive
apt-get update -y || true
apt-get install -y --no-install-recommends "${DPKG_OPTS[@]}" python3-apt || true

################################################################################
# 1. UPDATE SYSTEM (non-interactive)
################################################################################
echo -e "\n${BLUE}[1/8] Updating system packages...${NC}"
apt-get update -y
apt-get upgrade -y "${DPKG_OPTS[@]}"

################################################################################
# 2. INSTALL BASE DEPENDENCIES
################################################################################
echo -e "\n${BLUE}[2/8] Installing base dependencies...${NC}"
apt-get install -y --no-install-recommends "${DPKG_OPTS[@]}" \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    unzip \
    jq \
    htop \
    net-tools \
    nano \
    ansible \
    vim \
    python3-pip

################################################################################
# 3. INSTALL NODEJS (20.x)
################################################################################
echo -e "\n${BLUE}[3/8] Installing Node.js 20.x LTS...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
echo -e "${GREEN}✓ Node.js version:${NC} $(node -v || echo 'node not found')"
echo -e "${GREEN}✓ npm version:${NC} $(npm -v || echo 'npm not found')"
npm install -g pm2 || true
echo -e "${GREEN}✓ PM2 installed (if npm install succeeded)${NC}"

################################################################################
# 4. INSTALL PYTHON
################################################################################
echo -e "\n${BLUE}[4/8] Installing Python 3.10...${NC}"
apt-get install -y --no-install-recommends "${DPKG_OPTS[@]}" \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip

echo -e "${GREEN}✓ Python version:${NC} $(python3 --version 2>/dev/null || echo 'python3 not found')"
echo -e "${GREEN}✓ pip version:${NC} $(pip3 --version 2>/dev/null || echo 'pip3 not found')"

################################################################################
# 5. INSTALL DOCKER
################################################################################
echo -e "\n${BLUE}[5/8] Installing Docker and Docker Compose...${NC}"
# Remove old Docker packages if any
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install prerequisites
apt-get install -y --no-install-recommends "${DPKG_OPTS[@]}" ca-certificates gnupg

mkdir -p /etc/apt/keyrings
if [ -f "/etc/apt/keyrings/docker.gpg" ]; then
  rm /etc/apt/keyrings/docker.gpg
fi

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y --no-install-recommends "${DPKG_OPTS[@]}" docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable/start after cleanup (we blocked auto restarts)
echo -e "${YELLOW}Docker installed; will enable/start after cleanup${NC}"

################################################################################
# 6. INSTALL KUBERNETES TOOLS
################################################################################
echo -e "\n${BLUE}[6/8] Installing Kubernetes tools...${NC}"
if [ -f "/etc/apt/keyrings/kubernetes-apt-keyring.gpg" ]; then
  rm /etc/apt/keyrings/kubernetes-apt-keyring.gpg
fi


curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /" \
    | tee /etc/apt/sources.list.d/kubernetes.list

apt-get update -y
apt-get install -y --no-install-recommends "${DPKG_OPTS[@]}" kubectl

curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash || true

echo -e "${GREEN}✓ kubectl/helm installed (if their installs succeeded)${NC}"

################################################################################
# 7. INSTALL NGINX
################################################################################
echo -e "\n${BLUE}[7/8] Installing Nginx...${NC}"
apt-get install -y --no-install-recommends "${DPKG_OPTS[@]}" nginx
echo -e "${YELLOW}Nginx installed; will enable/start after cleanup${NC}"

################################################################################
# 8. INSTALL CERTBOT
################################################################################
echo -e "\n${BLUE}[8/8] Installing Certbot for SSL/TLS...${NC}"
apt-get install -y --no-install-recommends "${DPKG_OPTS[@]}" certbot python3-certbot-nginx || true
echo -e "${GREEN}✓ Certbot installation attempted${NC}"

################################################################################
# 8. INSTALL OLLAMA
################################################################################
echo -e "\n${BLUE}[8/8] Installing Ollama ...${NC}"
curl -fsSL https://ollama.com/install.sh | sh
systemctl start ollama
systemctl enable ollama
ollama pull llama3.1:8b
echo -e "${GREEN}✓ Installing Ollama Completed ${NC}"
################################################################################
# CREATE APP USER
################################################################################
echo -e "\n${BLUE}[*] Creating nimbusre app user...${NC}"
if ! id -u nimbusre > /dev/null 2>&1; then
    useradd -m -s /bin/bash -G docker nimbusre
    echo -e "${GREEN}✓ User 'nimbusre' created${NC}"
else
    echo -e "${YELLOW}! User 'nimbusre' already exists${NC}"
fi

################################################################################
# CLEANUP: remove policy-rc.d so services can be started, then explicitly start them
################################################################################
echo -e "\n${BLUE}Finalizing installation: enabling and starting services...${NC}"
# cleanup() will run on EXIT (trap), but remove here explicitly first to ensure services start now
if [[ -f "${POLICY_RC_D}" ]]; then
  rm -f "${POLICY_RC_D}" || true
  echo -e "${YELLOW}Temporary policy-rc.d removed${NC}"
fi

sudo systemctl daemon-reload || true

# Enable + start services we expect
for svc in docker nginx; do
  if systemctl list-unit-files | grep -q "^${svc}.service"; then
    systemctl enable "${svc}" || true
    systemctl restart "${svc}" || true
    echo -e "${GREEN}✓ ${svc} enabled/restarted${NC}"
  else
    echo -e "${YELLOW}! ${svc} unit not present (skipping)${NC}"
  fi
done

################################################################################
# SUMMARY
################################################################################
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}Installed / attempted components:${NC}"
echo "  ✓ Node.js 20.x LTS"
echo "  ✓ npm with PM2"
echo "  ✓ Python 3.10"
echo "  ✓ Docker & Docker Compose"
echo "  ✓ kubectl"
echo "  ✓ Helm"
echo "  ✓ Nginx"
echo "  ✓ Certbot (if available)"

echo -e "\n${BLUE}Useful checks:${NC}"
echo "  sudo systemctl status docker nginx"
echo "  docker --version"
echo "  kubectl version --client --short"
echo "  helm version --short"

echo -e "\n${GREEN}If any service failed to start, inspect the journal (e.g. sudo journalctl -u nginx -b)${NC}\n"

