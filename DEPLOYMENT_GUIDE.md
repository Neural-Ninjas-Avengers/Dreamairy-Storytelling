# 🚀 Claude Design Enhancement - Deployment Guide

## Production Deployment Checklist

### ✅ Pre-Deployment

#### 1. Environment Configuration
```bash
# backend/.env
AWS_REGION=eu-west-1
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
FLASK_ENV=production
DEBUG=False
```

#### 2. Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

#### 3. AWS Bedrock Access
- ✅ Verify AWS account has Bedrock access
- ✅ Enable Claude 3 Haiku model in AWS console
- ✅ Test credentials with admin panel
- ✅ Set appropriate IAM permissions

---

### 🔧 Configuration Steps

#### 1. Admin Panel Setup
1. Start backend: `python backend/app.py`
2. Open: `http://localhost:3001/admin/simple-admin.html`
3. Set environment to "Production"
4. Enter AWS credentials
5. Enable AWS services
6. Click "Save Configuration"
7. Test AWS connection

#### 2. Verify Integration
```bash
# Test Claude endpoint
curl -X POST http://localhost:3001/api/v1/design/claude/test

# Expected response:
{
  "success": true,
  "message": "Claude integration working correctly"
}
```

#### 3. Test Design Studio
1. Open: `http://localhost:3001/admin/design-studio.html`
2. Generate a color palette
3. Optimize a prompt
4. Generate an SVG
5. Verify all features work

---

### 🌐 Production Deployment

#### Option 1: Traditional Server

**Backend (Flask):**
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:3001 app:app
```

**Frontend (React):**
```bash
# Build production bundle
cd frontend
npm run build

# Serve with nginx or similar
# Point to frontend/build directory
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Admin panel
    location /admin {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
    }
}
```

#### Option 2: Docker

**Dockerfile (Backend):**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 3001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3001", "app:app"]
```

**Dockerfile (Frontend):**
```dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "3001:3001"
    environment:
      - AWS_REGION=${AWS_REGION}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - FLASK_ENV=production
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

#### Option 3: Cloud Platforms

**AWS Elastic Beanstalk:**
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.9 dreamairy-backend

# Create environment
eb create dreamairy-prod

# Deploy
eb deploy
```

**Heroku:**
```bash
# Create app
heroku create dreamairy-backend

# Set config
heroku config:set AWS_REGION=eu-west-1
heroku config:set AWS_ACCESS_KEY_ID=your_key
heroku config:set AWS_SECRET_ACCESS_KEY=your_secret

# Deploy
git push heroku main
```

**Vercel (Frontend):**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

---

### 🔒 Security Hardening

#### 1. Environment Variables
```bash
# NEVER commit these to git
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx

# Use environment-specific configs
# .env.production
# .env.staging
# .env.development
```

#### 2. CORS Configuration
```python
# backend/app.py
CORS(app, origins=[
    "https://your-domain.com",
    "https://www.your-domain.com"
])
```

#### 3. Rate Limiting
```python
# Already implemented:
# - Client-side: 10 req/min
# - Server-side: 10 req/min per session

# For production, consider:
# - Redis-based rate limiting
# - IP-based throttling
# - User-based quotas
```

#### 4. API Key Rotation
```bash
# Rotate AWS keys regularly
# Update in admin panel
# Restart backend
```

---

### 📊 Monitoring

#### 1. Logging
```python
# backend/app.py already logs:
# - All Claude API calls
# - Rate limit violations
# - Errors and exceptions

# Add production logging:
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. Cost Monitoring
```python
# Track Claude API usage
# Log costs per request
# Set up AWS CloudWatch alarms

# Example:
logger.info(f"Claude API call: {tokens_used} tokens, ~${cost:.4f}")
```

#### 3. Performance Monitoring
```python
# Track response times
# Monitor cache hit rates
# Alert on slow requests

# Example:
import time
start = time.time()
# ... API call ...
duration = time.time() - start
logger.info(f"Request took {duration:.2f}s")
```

---

### 🧪 Testing in Production

#### 1. Smoke Tests
```bash
# Test backend health
curl http://your-domain.com/health

# Test Claude endpoint
curl -X POST http://your-domain.com/api/v1/design/claude/status

# Test admin panel
curl http://your-domain.com/admin/simple-admin.html
```

#### 2. Load Testing
```bash
# Install Apache Bench
apt-get install apache2-utils

# Test palette generation
ab -n 100 -c 10 -p palette.json -T application/json \
   http://your-domain.com/api/v1/design/claude
```

#### 3. Integration Tests
```javascript
// Test full flow
const session = await createSession();
const palette = await generatePalette();
const prompt = await optimizePrompt();
const svg = await generateSVG();
```

---

### 💰 Cost Optimization

#### 1. Caching Strategy
```javascript
// Already implemented:
// - 1-hour TTL
// - 100 item limit
// - ~50% cost reduction

// For production:
// - Use Redis for distributed caching
// - Increase TTL for stable palettes
// - Pre-generate common themes
```

#### 2. Request Batching
```javascript
// Batch multiple requests
const results = await Promise.all([
  generatePalette(theme1, age1, goal1),
  generatePalette(theme2, age2, goal2),
  generatePalette(theme3, age3, goal3)
]);
```

#### 3. Fallback Usage
```javascript
// Use fallbacks for:
// - Development/testing
// - Demo accounts
// - Rate-limited users
// - Cost-sensitive scenarios
```

---

### 🔄 Rollback Plan

#### If Issues Occur:

1. **Disable Claude Integration:**
```python
# In admin panel:
# Set environment to "Demo"
# Disable AWS services
# App continues with fallbacks
```

2. **Revert Code:**
```bash
git revert <commit-hash>
git push origin main
```

3. **Restore Previous Version:**
```bash
# Docker
docker-compose down
docker-compose up -d --build

# Heroku
heroku rollback
```

---

### 📈 Scaling Considerations

#### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    # ... rest of config
```

#### Caching Layer
```python
# Use Redis for distributed caching
import redis
cache = redis.Redis(host='redis', port=6379)
```

#### CDN for Static Assets
```nginx
# Serve static files from CDN
location /static {
    proxy_pass https://cdn.your-domain.com;
}
```

---

### 🎯 Post-Deployment

#### 1. Verify Functionality
- ✅ Test color palette generation
- ✅ Test prompt optimization
- ✅ Test SVG generation
- ✅ Test Design Studio access
- ✅ Verify theme application in app

#### 2. Monitor Metrics
- 📊 API response times
- 💰 AWS costs
- 🔢 Request volumes
- ❌ Error rates
- 👥 User adoption

#### 3. Gather Feedback
- 📝 User surveys
- 🐛 Bug reports
- 💡 Feature requests
- 📈 Usage analytics

---

### 🆘 Troubleshooting

#### "Claude not available"
```bash
# Check AWS credentials
aws bedrock list-foundation-models --region eu-west-1

# Verify in admin panel
# Test endpoint: /api/v1/design/claude/test
```

#### "Rate limit exceeded"
```bash
# Check logs for abuse
# Increase limits if needed
# Implement user quotas
```

#### "High costs"
```bash
# Review cache hit rates
# Check for unnecessary requests
# Optimize prompt sizes
# Consider fallbacks for some users
```

---

### 📞 Support

#### Documentation
- Quick Start: `CLAUDE_DESIGN_QUICKSTART.md`
- Implementation: `IMPLEMENTATION_SUMMARY.md`
- API Docs: `backend/api/README_CLAUDE_DESIGN.md`
- Service Docs: `frontend/src/services/README_*.md`

#### Monitoring
- Backend logs: `backend/app.log`
- Browser console: Check for errors
- AWS CloudWatch: Monitor Bedrock usage

#### Contact
- GitHub Issues: For bugs and features
- Team Chat: For urgent issues
- Documentation: For how-to questions

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] AWS credentials configured
- [ ] Dependencies installed
- [ ] Environment variables set
- [ ] Tests passing
- [ ] Documentation reviewed

### Deployment
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Admin panel accessible
- [ ] Design Studio working
- [ ] Integration verified

### Post-Deployment
- [ ] Smoke tests passed
- [ ] Monitoring configured
- [ ] Costs tracked
- [ ] Team trained
- [ ] Users notified

---

**🚀 Ready for Production!**

*Follow this guide for a smooth deployment*
