# NimbusRE Agent Deployment Guide

This guide is aligned with the current shell scripts in this repository.

## Script Inventory

The following scripts exist and are covered here:

- Deploy_Scripts/install.sh
- Deploy_Scripts/install_tools.sh
- Deploy_Scripts/install_gcc_fix.sh
- Deploy_Scripts/deploy.sh
- Deploy_Scripts/deploy_app.sh
- Deploy_Scripts/setup-nginx.sh
- Deploy_Scripts/setup-ssl.sh
- Deploy_Scripts/manage.sh
- Deploy_Scripts/start_backend.sh

## Quick Decision Guide

Use this if you want a predictable setup without script mismatches:

1. Use Deploy_Scripts/install.sh for system dependencies.
2. Use Deploy_Scripts/deploy.sh for app deployment.
3. Use Deploy_Scripts/setup-nginx.sh for reverse proxy.
4. Use Deploy_Scripts/setup-ssl.sh only for public domains.
5. Use Deploy_Scripts/manage.sh for operations.

This path is internally consistent with backend port 8000.

## Important Compatibility Notes

There are two deployment variants in this repo:

- Deploy_Scripts/deploy.sh: backend on 8000
- Deploy_Scripts/deploy_app.sh: backend on 3001

And some ops scripts assume 8000:

- Deploy_Scripts/setup-nginx.sh proxies backend to 127.0.0.1:8000
- Deploy_Scripts/manage.sh health check uses http://localhost:8000/health

So if you choose Deploy_Scripts/deploy_app.sh, you must update Nginx and manage checks to 3001.

## Recommended Path (Stable Port 8000)

### 1) Install dependencies

Run as root:

```bash
sudo bash Deploy_Scripts/install.sh
```

What it installs:

- Node.js 20 and npm
- PM2 (global)
- Python 3.11 + venv/dev tools
- Docker + Compose plugin
- kubectl + Helm
- Nginx
- Certbot
- app user nimbusre (if missing)

### 2) Deploy application

Run from repository root (folder that contains frontend and src):

```bash
cd /path/to/kubetool
sudo bash Deploy_Scripts/deploy.sh
```

What it does:

- Copies project to /opt/nimbusre
- Creates Python virtual env and installs requirements
- Installs frontend dependencies and builds Next.js app
- Creates and enables systemd services:
  - nimbusre-backend on port 8000
  - nimbusre-frontend on port 3000
- Writes env files:
  - /opt/nimbusre/.env
  - /opt/nimbusre/frontend/.env.local

### 3) Configure Nginx (optional but recommended)

Localhost mode:

```bash
sudo bash Deploy_Scripts/setup-nginx.sh
```

Domain mode:

```bash
sudo bash Deploy_Scripts/setup-nginx.sh your-domain.com
```

### 4) Configure SSL (domain only)

```bash
sudo bash Deploy_Scripts/setup-ssl.sh your-domain.com
```

The script:

- Requests certs with certbot webroot
- Creates certbot-renew.service and certbot-renew.timer
- Reloads Nginx after renewal

### 5) Operate and monitor

```bash
sudo bash Deploy_Scripts/manage.sh
```

Menu options include:

- service status
- backend/frontend logs
- restart services
- health checks
- log cleanup
- config backup

## Alternative AWS-Oriented Path (Non-Interactive)

Use this when you need package installation that avoids interactive apt prompts:

```bash
sudo bash Deploy_Scripts/install_tools.sh
```

Key differences from Deploy_Scripts/install.sh:

- Uses DEBIAN_FRONTEND=noninteractive and dpkg force-conf options
- Installs Python 3.10 (not 3.11)
- Installs ansible
- Installs and enables ollama, then pulls llama3.1:8b
- Uses temporary policy-rc.d logic to suppress service restart prompts

Deploy option in this path:

```bash
sudo bash Deploy_Scripts/deploy_app.sh
```

Important differences in Deploy_Scripts/deploy_app.sh:

- backend runs on 3001
- uses rsync with delete semantics into /opt/nimbusre
- runs aws eks update-kubeconfig command at end
- copies ~/.kube/config to /opt/nimbusre/docker-desktop-config.yaml

If you use Deploy_Scripts/deploy_app.sh, also update these assumptions:

- Deploy_Scripts/setup-nginx.sh upstream backend port (8000 -> 3001)
- Deploy_Scripts/manage.sh health check endpoint port (8000 -> 3001)

## Script-by-Script Reference

## Deploy_Scripts/install.sh

Purpose: default full Ubuntu install.

Run:

```bash
sudo bash Deploy_Scripts/install.sh
```

## Deploy_Scripts/install_tools.sh

Purpose: non-interactive/AWS-friendly installer and ollama setup.

Run:

```bash
sudo bash Deploy_Scripts/install_tools.sh
```

## Deploy_Scripts/install_gcc_fix.sh

Purpose: NVIDIA DKMS/GCC repair helper.

Use only for host-level compiler/module repair.

Run:

```bash
sudo bash Deploy_Scripts/install_gcc_fix.sh
```

Notes:

- attempts gcc-12 first, then gcc-13 fallback
- targets DKMS module version nvidia 590.48.01

## Deploy_Scripts/deploy.sh

Purpose: standard deployment path, backend on 8000.

Run:

```bash
sudo bash Deploy_Scripts/deploy.sh
```

## Deploy_Scripts/deploy_app.sh

Purpose: alternate deployment script, backend on 3001.

Run:

```bash
sudo bash Deploy_Scripts/deploy_app.sh
```

Notes:

- assumes AWS CLI setup for eks update-kubeconfig
- may require additional updates in Nginx/manage script checks

## Deploy_Scripts/setup-nginx.sh

Purpose: configure reverse proxy for frontend and backend.

Run:

```bash
sudo bash Deploy_Scripts/setup-nginx.sh
sudo bash Deploy_Scripts/setup-nginx.sh your-domain.com
```

Current backend upstream target in script: 127.0.0.1:8000

## Deploy_Scripts/setup-ssl.sh

Purpose: issue Lets Encrypt certificates and configure renewal timer.

Run:

```bash
sudo bash Deploy_Scripts/setup-ssl.sh your-domain.com
```

## Deploy_Scripts/manage.sh

Purpose: interactive operations and monitoring menu.

Run:

```bash
sudo bash Deploy_Scripts/manage.sh
```

Current health check target in script: http://localhost:8000/health

## Deploy_Scripts/start_backend.sh

Purpose: local/dev helper only.

Warning:

- starts from repository root relative to Deploy_Scripts folder
- starts server directly with python src/api/api_server.py
- not suitable for production deployment

## Ports and Endpoints

For the recommended stable path (Deploy_Scripts/install.sh + Deploy_Scripts/deploy.sh):

- frontend: 3000
- backend: 8000
- docs: http://localhost:8000/docs
- health: http://localhost:8000/health

For Deploy_Scripts/deploy_app.sh path:

- frontend: 3000
- backend: 3001
- docs: http://localhost:3001/docs
- health: http://localhost:3001/health

## Systemd Services

- nimbusre-backend
- nimbusre-frontend
- nginx
- docker
- certbot-renew.timer (after Deploy_Scripts/setup-ssl.sh)

Useful commands:

```bash
sudo systemctl status nimbusre-backend nimbusre-frontend
sudo journalctl -u nimbusre-backend -f
sudo journalctl -u nimbusre-frontend -f
sudo nginx -t
sudo systemctl reload nginx
```

## Common Troubleshooting

### Deployment fails when copying files

Ensure you run deploy script from repo root:

```bash
cd /path/to/kubetool
sudo bash Deploy_Scripts/deploy.sh
```

### Backend unhealthy behind Nginx

Check backend port alignment:

- Deploy_Scripts/deploy.sh expects 8000
- Deploy_Scripts/deploy_app.sh expects 3001

Then verify:

```bash
sudo systemctl status nimbusre-backend
curl -i http://localhost:8000/health
curl -i http://localhost:3001/health
```

### SSL issuance fails

Verify:

- DNS points to this host
- port 80 reachable from internet
- Nginx is active

Then retry:

```bash
sudo certbot certificates
sudo bash Deploy_Scripts/setup-ssl.sh your-domain.com
```

## Production Checklist

- install script completed successfully
- deployment script completed successfully
- service status all green
- backend health endpoint responds
- Nginx config test passes
- SSL cert and renewal timer active (if domain)
- kubeconfig set for runtime user when using Kubernetes tools
