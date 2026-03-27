#!/bin/bash

################################################################################
# NimbusRE Agent - Ubuntu Installation Script
# Installs all system dependencies, Node.js, Python, Docker, and required tools
################################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}NimbusRE Agent - Installation Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
    echo "Please run: sudo bash Deploy_Scripts/install.sh"
   exit 1
fi

# Get Ubuntu version
OS_VERSION=$(lsb_release -rs)
echo -e "${YELLOW}[*] Detected Ubuntu ${OS_VERSION}${NC}"

################################################################################
# 1. UPDATE SYSTEM
################################################################################
echo -e "\n${BLUE}[1/8] Updating system packages...${NC}"
apt update
apt upgrade -y

################################################################################
# 2. INSTALL BASE DEPENDENCIES
################################################################################
echo -e "\n${BLUE}[2/8] Installing base dependencies...${NC}"
apt install -y \
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
    vim

################################################################################
# 3. INSTALL NODEJS
################################################################################
echo -e "\n${BLUE}[3/8] Installing Node.js 20.x LTS...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

echo -e "${GREEN}✓ Node.js version:${NC} $(node -v)"
echo -e "${GREEN}✓ npm version:${NC} $(npm -v)"

# Install PM2 globally
npm install -g pm2
echo -e "${GREEN}✓ PM2 installed globally${NC}"

################################################################################
# 4. INSTALL PYTHON
################################################################################
echo -e "\n${BLUE}[4/8] Installing Python 3.11...${NC}"
apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip

# Set Python3.11 as default python3
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

echo -e "${GREEN}✓ Python version:${NC} $(python3 --version)"
echo -e "${GREEN}✓ pip version:${NC} $(pip3 --version)"

################################################################################
# 5. INSTALL DOCKER
################################################################################
echo -e "\n${BLUE}[5/8] Installing Docker and Docker Compose...${NC}"

# Remove old Docker installations
apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Add Docker GPG key
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker service
systemctl enable docker
systemctl start docker

echo -e "${GREEN}✓ Docker version:${NC} $(docker --version)"
echo -e "${GREEN}✓ Docker Compose version:${NC} $(docker compose version)"

################################################################################
# 6. INSTALL KUBERNETES TOOLS
################################################################################
echo -e "\n${BLUE}[6/8] Installing Kubernetes tools...${NC}"

# Install kubectl
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /" | \
    tee /etc/apt/sources.list.d/kubernetes.list

apt update
apt install -y kubectl

echo -e "${GREEN}✓ kubectl version:${NC} $(kubectl version --client --short 2>/dev/null || echo 'installed')"

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo -e "${GREEN}✓ Helm version:${NC} $(helm version --short)"

################################################################################
# 7. INSTALL NGINX
################################################################################
echo -e "\n${BLUE}[7/8] Installing Nginx...${NC}"
apt install -y nginx

systemctl enable nginx
systemctl start nginx

echo -e "${GREEN}✓ Nginx installed${NC}"

################################################################################
# 8. INSTALL CERTBOT FOR SSL
################################################################################
echo -e "\n${BLUE}[8/8] Installing Certbot for SSL/TLS...${NC}"
apt install -y certbot python3-certbot-nginx

echo -e "${GREEN}✓ Certbot installed${NC}"

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
# SUMMARY
################################################################################
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}Installed Components:${NC}"
echo "  ✓ Node.js 20.x LTS"
echo "  ✓ npm with PM2"
echo "  ✓ Python 3.11"
echo "  ✓ Docker & Docker Compose"
echo "  ✓ kubectl"
echo "  ✓ Helm"
echo "  ✓ Nginx"
echo "  ✓ Certbot (SSL/TLS)"

echo -e "\n${BLUE}Next Steps:${NC}"
echo "  1. Run: sudo bash Deploy_Scripts/deploy.sh"
echo "  2. Configure Nginx: sudo bash Deploy_Scripts/setup-nginx.sh"
echo "  3. Set up SSL: sudo bash Deploy_Scripts/setup-ssl.sh <your-domain>"
echo "  4. Access app at: http://localhost or https://your-domain"

echo -e "\n${BLUE}Useful Commands:${NC}"
echo "  sudo systemctl status nimbusre-backend"
echo "  sudo systemctl status nimbusre-frontend"
echo "  pm2 logs nimbusre-frontend"
echo "  docker ps"
echo "  kubectl get pods"

echo -e "\n${GREEN}For more info, see DEPLOYMENT_GUIDE.md${NC}\n"
