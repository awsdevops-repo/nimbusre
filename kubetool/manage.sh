#!/bin/bash

################################################################################
# NimbusRE Agent - Monitoring & Maintenance Script
# Health checks, log management, and system monitoring
################################################################################

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

APP_DIR="/opt/nimbusre"
APP_USER="nimbusre"

################################################################################
# FUNCTIONS
################################################################################

show_menu() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}NimbusRE Agent - Monitoring & Maintenance${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    echo "1. Check service status"
    echo "2. View backend logs (live)"
    echo "3. View frontend logs (live)"
    echo "4. View error logs (Nginx)"
    echo "5. Restart all services"
    echo "6. Check system resources"
    echo "7. Check API health"
    echo "8. Clean logs"
    echo "9. Database backup"
    echo "10. View configuration"
    echo "0. Exit"
    echo ""
}

check_status() {
    echo -e "\n${BLUE}Service Status:${NC}\n"
    
    echo "Backend Service:"
    systemctl is-active --quiet nimbusre-backend && echo -e "${GREEN}  ✓ Running${NC}" || echo -e "${RED}  ✗ Stopped${NC}"
    systemctl is-enabled --quiet nimbusre-backend && echo -e "${GREEN}  ✓ Enabled on boot${NC}" || echo -e "${YELLOW}  ! Disabled on boot${NC}"
    
    echo -e "\nFrontend Service:"
    systemctl is-active --quiet nimbusre-frontend && echo -e "${GREEN}  ✓ Running${NC}" || echo -e "${RED}  ✗ Stopped${NC}"
    systemctl is-enabled --quiet nimbusre-frontend && echo -e "${GREEN}  ✓ Enabled on boot${NC}" || echo -e "${YELLOW}  ! Disabled on boot${NC}"
    
    echo -e "\nNginx:"
    systemctl is-active --quiet nginx && echo -e "${GREEN}  ✓ Running${NC}" || echo -e "${RED}  ✗ Stopped${NC}"
    
    echo -e "\nDocker:"
    systemctl is-active --quiet docker && echo -e "${GREEN}  ✓ Running${NC}" || echo -e "${RED}  ✗ Stopped${NC}"
    
    echo -e "\nOpen Ports:"
    netstat -tlnp 2>/dev/null | grep -E ':3000|:8000|:80|:443' | awk '{print "  " $4, "(" $7 ")"}' || echo "  (Check with: sudo netstat -tlnp)"
    
    echo ""
}

view_backend_logs() {
    echo -e "\n${BLUE}Backend Logs (Press Ctrl+C to exit):${NC}\n"
    sudo journalctl -u nimbusre-backend -f --lines=50
}

view_frontend_logs() {
    echo -e "\n${BLUE}Frontend Logs (Press Ctrl+C to exit):${NC}\n"
    sudo journalctl -u nimbusre-frontend -f --lines=50
}

view_error_logs() {
    echo -e "\n${BLUE}Nginx Error Logs (Press Ctrl+C to exit):${NC}\n"
    tail -f /var/log/nginx/nimbusre-error.log
}

restart_services() {
    echo -e "\n${YELLOW}Restarting all services...${NC}\n"
    
    echo "Restarting backend..."
    sudo systemctl restart nimbusre-backend
    sleep 2
    
    echo "Restarting frontend..."
    sudo systemctl restart nimbusre-frontend
    sleep 2
    
    echo "Reloading Nginx..."
    sudo systemctl reload nginx
    
    echo -e "\n${GREEN}✓ All services restarted${NC}\n"
    check_status
}

check_resources() {
    echo -e "\n${BLUE}System Resources:${NC}\n"
    
    echo "CPU Usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print "  " $0}'
    
    echo -e "\nMemory Usage:"
    free -h | tail -2 | awk '{print "  " $0}'
    
    echo -e "\nDisk Usage:"
    df -h /opt/nimbusre | awk 'NR==2 {printf "  Used: %s / %s (%.1f%%)\n", $3, $2, $5}'
    
    echo -e "\nProcess Memory (Backend):"
    ps aux | grep "python.*api_server" | grep -v grep | awk '{printf "  PID %s: %s MB\n", $2, $6}'
    
    echo -e "\nProcess Memory (Frontend):"
    ps aux | grep "node" | grep -v grep | awk '{printf "  PID %s: %s MB\n", $2, $6}'
    
    echo ""
}

check_health() {
    echo -e "\n${BLUE}API Health Check:${NC}\n"
    
    echo "Backend API:"
    if curl -s http://localhost:8000/health &>/dev/null; then
        echo -e "  ${GREEN}✓ Responding${NC}"
        curl -s http://localhost:8000/docs -I | head -1
    else
        echo -e "  ${RED}✗ Not responding${NC}"
    fi
    
    echo -e "\nFrontend:"
    if curl -s http://localhost:3000 &>/dev/null; then
        echo -e "  ${GREEN}✓ Responding${NC}"
    else
        echo -e "  ${RED}✗ Not responding${NC}"
    fi
    
    echo -e "\nNginx Proxy:"
    if curl -s http://localhost/ &>/dev/null; then
        echo -e "  ${GREEN}✓ Responding${NC}"
    else
        echo -e "  ${RED}✗ Not responding${NC}"
    fi
    
    echo ""
}

clean_logs() {
    echo -e "\n${YELLOW}Cleaning old log files...${NC}\n"
    
    # Clean systemd journal (keep last 100MB)
    sudo journalctl --vacuum=100M
    echo -e "${GREEN}✓ Cleaned systemd journal${NC}"
    
    # Rotate nginx logs
    sudo logrotate -f /etc/logrotate.d/nginx 2>/dev/null || true
    echo -e "${GREEN}✓ Rotated Nginx logs${NC}"
    
    echo ""
}

backup_config() {
    echo -e "\n${BLUE}Configuration Backup:${NC}\n"
    
    BACKUP_DIR="/opt/nimbusre/backups"
    mkdir -p $BACKUP_DIR
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    echo "Backing up configuration..."
    tar -czf $BACKUP_DIR/nimbusre-config-$TIMESTAMP.tar.gz \
        -C /opt/nimbusre .env frontend/.env.local 2>/dev/null
    
    echo "Backing up application..."
    tar -czf $BACKUP_DIR/nimbusre-app-$TIMESTAMP.tar.gz \
        -C /opt/nimbusre src/ --exclude='__pycache__' \
        --exclude='.git' 2>/dev/null
    
    echo -e "${GREEN}✓ Backups created in $BACKUP_DIR${NC}\n"
    
    ls -lh $BACKUP_DIR | tail -5
    echo ""
}

view_config() {
    echo -e "\n${BLUE}Configuration Files:${NC}\n"
    
    echo "Backend (.env):"
    if [ -f /opt/nimbusre/.env ]; then
        cat /opt/nimbusre/.env | sed 's/^/  /'
    else
        echo "  Not found"
    fi
    
    echo -e "\nFrontend (.env.local):"
    if [ -f /opt/nimbusre/frontend/.env.local ]; then
        cat /opt/nimbusre/frontend/.env.local | sed 's/^/  /'
    else
        echo "  Not found"
    fi
    
    echo ""
}

################################################################################
# MAIN LOOP
################################################################################

while true; do
    show_menu
    read -p "Select option: " option
    
    case $option in
        1) check_status ;;
        2) view_backend_logs ;;
        3) view_frontend_logs ;;
        4) view_error_logs ;;
        5) restart_services ;;
        6) check_resources ;;
        7) check_health ;;
        8) clean_logs ;;
        9) backup_config ;;
        10) view_config ;;
        0) echo -e "\n${GREEN}Goodbye!${NC}\n"; exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
    
    read -p "Press Enter to continue..."
done
