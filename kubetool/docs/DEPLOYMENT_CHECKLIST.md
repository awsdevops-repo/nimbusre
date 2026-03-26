# SREAgent Deployment Checklist

Use this checklist to ensure your SREAgent deployment is complete and production-ready.

## Pre-Deployment

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed
- [ ] kubectl configured and tested
- [ ] Ollama running with llama2 model
- [ ] Kubernetes cluster accessible
- [ ] Prometheus running (for monitoring_tool)

### Repository Setup
- [ ] Project cloned/downloaded
- [ ] `requirements.txt` dependencies documented
- [ ] `frontend/package.json` dependencies documented
- [ ] Git repository initialized (if using version control)
- [ ] `.gitignore` configured

## Backend Deployment

### Local Development
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `api_server.py` tested locally (`python api_server.py`)
- [ ] API responds to health check (`curl http://localhost:3001/health`)
- [ ] API documentation visible (`http://localhost:3001/docs`)

### Docker Setup
- [ ] Dockerfile created and tested
- [ ] Docker image builds successfully (`docker build -t sreagent-backend:1.0 .`)
- [ ] Container runs (`docker run -p 3001:3001 sreagent-backend:1.0`)
- [ ] Health check passes in container

### Configuration
- [ ] Kubernetes kubeconfig accessible
- [ ] kubectl commands work from backend environment
- [ ] Ollama API accessible from backend
- [ ] Prometheus accessible (if using monitoring_tool)
- [ ] Environment variables documented

### Security
- [ ] Input validation enabled
- [ ] Protected namespaces configured
- [ ] Grace periods set for pod termination
- [ ] RBAC kubeconfig created
- [ ] Error messages don't leak sensitive data
- [ ] Logs don't contain credentials

## Frontend Deployment

### Local Development
- [ ] Dependencies installed (`npm install`)
- [ ] Development server runs (`npm run dev`)
- [ ] Frontend loads at `http://localhost:3000`
- [ ] Chat interface responsive
- [ ] Dark mode works
- [ ] Can send test queries

### Build
- [ ] Build succeeds (`npm run build`)
- [ ] No TypeScript errors
- [ ] No console errors
- [ ] Images optimized
- [ ] Assets bundled correctly

### Docker Setup
- [ ] Dockerfile created and tested
- [ ] Docker image builds (`docker build -t sreagent-frontend:1.0 ./frontend`)
- [ ] Container runs (`docker run -p 3000:3000 sreagent-frontend:1.0`)
- [ ] Health check passes
- [ ] Can access frontend in container

### Configuration
- [ ] `.env.local` configured with backend URL
- [ ] Environment variables documented
- [ ] API endpoint accessible from frontend
- [ ] CORS properly configured

### UI/UX
- [ ] Chat interface functional
- [ ] Quick action buttons work
- [ ] Example queries display
- [ ] Findings panel displays correctly
- [ ] Status panel shows workflow info
- [ ] Error messages clear and helpful

## Multi-Container Setup

### Docker Compose
- [ ] `docker-compose.yml` created
- [ ] All services defined
- [ ] Networks configured
- [ ] Volumes mounted correctly
- [ ] Health checks defined
- [ ] Dependencies specified

### Running
- [ ] Services start (`docker-compose up -d`)
- [ ] All services healthy (`docker-compose ps`)
- [ ] Frontend connects to backend
- [ ] Logs accessible (`docker-compose logs -f`)
- [ ] Services stop cleanly (`docker-compose down`)

## Testing

### Functional Tests
- [ ] Can query "Show health"
- [ ] Can query CPU metrics
- [ ] Can get pod logs
- [ ] Can restart pod (Advanced mode)
- [ ] Can analyze costs
- [ ] Findings display correctly
- [ ] Status updates show

### Integration Tests
- [ ] Backend connects to Kubernetes
- [ ] Backend connects to Prometheus
- [ ] Backend connects to Ollama
- [ ] Frontend connects to backend API
- [ ] Logs accessible from frontend
- [ ] Metrics accessible from frontend

### Error Handling
- [ ] Invalid query handled gracefully
- [ ] Network timeout handled
- [ ] Kubernetes error handled
- [ ] Ollama error handled
- [ ] User error messages clear

### Performance
- [ ] Response time < 20 seconds (basic)
- [ ] Response time < 30 seconds (advanced)
- [ ] UI responsive during queries
- [ ] No memory leaks
- [ ] Logs don't grow unbounded

## Documentation

### Setup
- [ ] QUICK_START.md accurate
- [ ] SETUP_AND_DEPLOYMENT.md complete
- [ ] Dependencies listed
- [ ] Prerequisites documented
- [ ] Troubleshooting section updated

### API
- [ ] `/docs` endpoint working
- [ ] All endpoints documented
- [ ] Request/response examples given
- [ ] Error codes documented

### User Guide
- [ ] Example queries documented
- [ ] Workflow types explained
- [ ] Security best practices listed
- [ ] Integration examples provided

## Production Deployment

### Kubernetes
- [ ] Namespace created (`kubectl create namespace sreagent`)
- [ ] RBAC roles configured
- [ ] Deployment manifests created
- [ ] ConfigMaps/Secrets created (if needed)
- [ ] Ingress configured (if needed)
- [ ] PersistentVolumes configured (if needed)
- [ ] Deployed successfully (`kubectl apply -f ...`)

### Scaling
- [ ] Horizontal Pod Autoscaling (HPA) configured
- [ ] Load balancer configured
- [ ] Service discovery working
- [ ] DNS working

### Monitoring
- [ ] Prometheus scraping metrics
- [ ] Loki collecting logs
- [ ] Alerts configured
- [ ] Dashboard created
- [ ] Health checks working

### Backup & Recovery
- [ ] Backup strategy defined
- [ ] Database backups scheduled (if using)
- [ ] Disaster recovery plan documented
- [ ] Recovery tested

## Security

### Network Security
- [ ] Firewall rules configured
- [ ] HTTPS enabled
- [ ] TLS certificates valid
- [ ] Ingress TLS configured
- [ ] Network policies applied

### Access Control
- [ ] RBAC configured
- [ ] Users/roles defined
- [ ] Authentication enabled
- [ ] Authorization working
- [ ] Audit logging enabled

### Data Protection
- [ ] Sensitive data encrypted
- [ ] Secrets managed securely
- [ ] kubeconfig permissions restricted
- [ ] No credentials in logs
- [ ] No secrets in environment variables

### Compliance
- [ ] Security policy documented
- [ ] Data retention policy defined
- [ ] Audit trail maintained
- [ ] Compliance requirements met

## Monitoring & Logging

### Backend Monitoring
- [ ] Application metrics exported
- [ ] Request latency tracked
- [ ] Error rates monitored
- [ ] Resource usage tracked
- [ ] Health checks passing

### Frontend Monitoring
- [ ] Performance metrics collected
- [ ] Error tracking enabled
- [ ] User analytics (if applicable)
- [ ] Load times tracked

### Logging
- [ ] Logs centralized
- [ ] Log retention configured
- [ ] Log levels appropriate
- [ ] Sensitive data not logged
- [ ] Logs searchable

## Integration

### External Systems
- [ ] Slack notifications configured (optional)
- [ ] PagerDuty integration configured (optional)
- [ ] Email alerts configured (optional)
- [ ] Webhooks configured (optional)

### Monitoring Systems
- [ ] Prometheus integration working
- [ ] Grafana dashboards created
- [ ] Alert rules configured
- [ ] Incident response workflows ready

## Handoff

### Documentation
- [ ] All documentation updated
- [ ] Architecture documented
- [ ] Deployment documented
- [ ] Operations manual created
- [ ] Runbooks created

### Team Knowledge
- [ ] Team trained on system
- [ ] On-call rotation established
- [ ] Escalation procedures documented
- [ ] Common issues documented

### Support
- [ ] Support contact defined
- [ ] Escalation process documented
- [ ] SLA defined
- [ ] Issue tracking configured

## Post-Deployment

### Validation
- [ ] System running stably (24 hours)
- [ ] No critical errors in logs
- [ ] Performance metrics normal
- [ ] Users can access system
- [ ] All features working

### Optimization
- [ ] Cache hits optimized
- [ ] Query performance optimized
- [ ] Resource usage optimized
- [ ] Cost optimized

### Feedback
- [ ] User feedback collected
- [ ] Issues documented
- [ ] Improvements identified
- [ ] Next iteration planned

---

## Quick Deployment Commands

### Docker Compose Quick Start
```bash
cd kubetool
docker-compose up -d
docker-compose logs -f
# Access at http://localhost:3000
```

### Kubernetes Quick Deploy
```bash
kubectl create namespace sreagent
kubectl apply -f sreagent-deployment.yaml
kubectl get pods -n sreagent
kubectl port-forward -n sreagent svc/sreagent-frontend 3000:3000
```

### Development Quick Start
```bash
# Terminal 1
cd kubetool && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python api_server.py

# Terminal 2
cd kubetool/frontend && npm install && npm run dev

# Open http://localhost:3000
```

---

## Troubleshooting Reference

| Issue | Solution | Checklist Item |
|-------|----------|---|
| Backend won't start | Check Python dependencies | Backend Deployment |
| Frontend can't connect | Check backend URL in .env.local | Frontend Configuration |
| Kubernetes connection fails | Verify kubeconfig | Backend Configuration |
| Ollama not responding | Start Ollama service | Pre-Deployment |
| Metrics not available | Check Prometheus running | Pre-Deployment |
| Container won't start | Check Docker logs | Docker Setup |
| API returns errors | Check error logs | Testing |

---

## Estimated Timeline

- **Setup**: 30 minutes
- **Testing**: 1 hour
- **Documentation**: 30 minutes
- **First deployment**: 1 hour
- **Production hardening**: 2-4 hours
- **Total**: 5-7 hours for full deployment

---

## Sign-Off

- [ ] Project Lead: _______________  Date: _______
- [ ] DevOps Lead: _______________  Date: _______
- [ ] Security Lead: _______________  Date: _______
- [ ] QA Lead: _______________  Date: _______

---

## Notes

```
[Space for additional notes and customizations]




```

---

Last Updated: [Current Date]
Ready for Deployment: [ ] Yes [ ] No
