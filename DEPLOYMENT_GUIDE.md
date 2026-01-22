# 🚀 Flexa ChatBot Deployment Guide

## Overview
Flexa is a full-stack AI fitness chatbot application consisting of:
- **Frontend**: React.js application (runs on port 3000)
- **Backend**: FastAPI Python server with ML model (runs on port 5000)
- **ML Model**: Scikit-learn trained model (flexa_plan_model.joblib)

## Table of Contents
1. [Deployment Options](#deployment-options)
2. [Option 1: Vercel + Render (Recommended - FREE)](#option-1-vercel--render-recommended---free)
3. [Option 2: Heroku](#option-2-heroku)
4. [Option 3: AWS](#option-3-aws)
5. [Option 4: DigitalOcean](#option-4-digitalocean)
6. [Option 5: Docker](#option-5-docker)
7. [Environment Configuration](#environment-configuration)
8. [Domain Setup](#domain-setup)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## Deployment Options

### Cost & Feature Comparison

| Platform | Frontend Cost | Backend Cost | Total/Month | Difficulty | Best For |
|----------|--------------|--------------|-------------|------------|----------|
| **Vercel + Render** | Free | Free* | $0-7 | Easy | Side projects, MVPs |
| **Heroku** | $7 | $7 | $14 | Easy | Quick deployment |
| **DigitalOcean** | $5 | $5 | $10 | Medium | Cost-effective |
| **AWS** | $1-5 | $10-20 | $11-25 | Hard | Scalability |
| **Docker (Any)** | Varies | Varies | $5-50+ | Medium | Flexibility |

*Render free tier has limitations: 750 hours/month, sleeps after inactivity

---

## Option 1: Vercel + Render (Recommended - FREE)

### Why This Option?
- ✅ **Free tier** for both services
- ✅ **Easy deployment** from GitHub
- ✅ **Auto HTTPS** included
- ✅ **Fast CDN** for frontend
- ✅ **Good for learning** and MVPs

### Prerequisites
- GitHub account
- Git installed
- Node.js and npm installed
- Python 3.10+

---

### Step 1: Prepare Your Code

#### 1.1 Initialize Git Repository
```bash
cd Flexa-ChatBot
git init
git add .
git commit -m "Initial commit - Flexa AI Chatbot"
```

#### 1.2 Create GitHub Repository
1. Go to https://github.com/new
2. Create new repository: `flexa-chatbot`
3. Don't initialize with README (we already have code)

#### 1.3 Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/flexa-chatbot.git
git branch -M main
git push -u origin main
```

---

### Step 2: Deploy Backend to Render

#### 2.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Authorize Render to access your repositories

#### 2.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select `flexa-chatbot` repository

#### 2.3 Configure Backend Service
Fill in the following settings:

**Basic Settings:**
- **Name**: `flexa-backend`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: `flexa-backendnew-main`

**Build Settings:**
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Environment Variables:**
- Click **"Add Environment Variable"**
- Add: `PYTHON_VERSION` = `3.10.0`

**Instance Type:**
- Select **"Free"** (750 hours/month)

#### 2.4 Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Once deployed, you'll see: ✅ **Live**
4. **Copy your backend URL**: `https://flexa-backend.onrender.com`

#### 2.5 Test Backend
Open in browser:
```
https://flexa-backend.onrender.com/docs
```
You should see the FastAPI documentation page.

---

### Step 3: Update Frontend Configuration

#### 3.1 Create Environment File
```bash
cd flexa-frontend-main
```

Create `.env.production`:
```env
REACT_APP_API_URL=https://flexa-backend.onrender.com
```

#### 3.2 Update API Calls in Code

**Option A: Using Environment Variable (Recommended)**

Edit `src/pages/Chat.js`:

```javascript
// Add at the top of the file
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Update all fetch calls to use API_URL
const startChat = async () => {
  try {
    const response = await fetch(`${API_URL}/chat/start`);
    // ... rest of code
  }
};

const sendMessage = async () => {
  // ...
  const response = await fetch(`${API_URL}/chat/message`, {
    // ... rest of code
  });
};
```

**Option B: Direct URL Replacement**

Replace all instances of `http://localhost:5000` with your Render URL:
```javascript
// Find and replace
'http://localhost:5000' → 'https://flexa-backend.onrender.com'
```

#### 3.3 Update CORS in Backend

Edit `flexa-backendnew-main/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://flexa-frontend.vercel.app",  # Update with your Vercel domain
        "http://localhost:3000",  # Keep for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push changes:
```bash
git add .
git commit -m "Update API URL for production"
git push
```

Render will auto-deploy the backend update.

---

### Step 4: Deploy Frontend to Vercel

#### 4.1 Install Vercel CLI
```bash
npm install -g vercel
```

#### 4.2 Login to Vercel
```bash
vercel login
```
Follow the prompts to authenticate.

#### 4.3 Deploy Frontend
```bash
cd flexa-frontend-main
vercel
```

**Answer the prompts:**
- Set up and deploy?: **Y**
- Which scope?: Select your account
- Link to existing project?: **N**
- What's your project's name?: `flexa-frontend`
- In which directory is your code located?: `./`
- Want to modify settings?: **N**

Wait for deployment to complete.

#### 4.4 Deploy to Production
```bash
vercel --prod
```

You'll get a URL like: `https://flexa-frontend.vercel.app`

#### 4.5 Update Backend CORS
Go back to your backend code and update the CORS origins with your actual Vercel URL, then push:

```python
allow_origins=[
    "https://flexa-frontend.vercel.app",  # Your actual Vercel URL
    "http://localhost:3000",
],
```

```bash
git add .
git commit -m "Update CORS with Vercel domain"
git push
```

---

### Step 5: Test Your Deployed App

1. Open your Vercel URL: `https://flexa-frontend.vercel.app`
2. Click "Start Chatting" or navigate to `/chat`
3. Test the complete flow:
   - Name inputconsole.log('Session ID:', sessionStorage.getItem('sessionId'))
   - Problem description
   - Sex, Age, Height, Weight
   - Health conditions
   - Receive ML recommendations
   - Video suggestions

**Important Notes:**
- ⚠️ First request to Render may take 30-60 seconds (free tier spins down)
- ⚠️ Backend wakes up after ~15 minutes of inactivity
- ✅ Subsequent requests are fast

---

## Option 2: Heroku

### Prerequisites
- Heroku account
- Heroku CLI installed

### Backend Deployment

#### 2.1 Create Procfile
Create `flexa-backendnew-main/Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 2.2 Create runtime.txt
Create `flexa-backendnew-main/runtime.txt`:
```
python-3.10.0
```

#### 2.3 Deploy Backend
```bash
cd flexa-backendnew-main
heroku login
heroku create flexa-backend
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a flexa-backend
git push heroku main
```

#### 2.4 Get Backend URL
```bash
heroku open
```
Copy the URL: `https://flexa-backend.herokuapp.com`

### Frontend Deployment

#### 2.5 Update Frontend API URL
Same as Vercel steps - update API calls to use Heroku backend URL.

#### 2.6 Deploy Frontend to Heroku
```bash
cd flexa-frontend-main
heroku create flexa-frontend
heroku buildpacks:set mars/create-react-app
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a flexa-frontend
git push heroku main
```

**Cost:** $7/month per dyno = $14/month total

---

## Option 3: AWS

### Architecture
- **Frontend**: S3 + CloudFront
- **Backend**: EC2 or Elastic Beanstalk
- **Database** (if needed): RDS

### Frontend on S3 + CloudFront

#### 3.1 Build React App
```bash
cd flexa-frontend-main
npm run build
```

#### 3.2 Create S3 Bucket
1. Go to AWS S3 Console
2. Create bucket: `flexa-frontend`
3. Enable static website hosting
4. Set index document: `index.html`
5. Upload `build/` folder contents

#### 3.3 Configure Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::flexa-frontend/*"
    }
  ]
}
```

#### 3.4 Add CloudFront (Optional)
1. Create CloudFront distribution
2. Origin: Your S3 bucket
3. Enable HTTPS
4. Wait for distribution to deploy

### Backend on EC2

#### 3.5 Launch EC2 Instance
1. Choose Ubuntu Server 22.04
2. Instance type: t2.micro (free tier)
3. Configure security group:
   - SSH (22)
   - HTTP (80)
   - HTTPS (443)
   - Custom TCP (5000)

#### 3.6 Connect and Setup
```bash
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3-pip python3-venv -y

# Clone your repository
git clone https://github.com/YOUR_USERNAME/flexa-chatbot.git
cd flexa-chatbot/flexa-backendnew-main

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install nginx
sudo apt install nginx -y

# Install supervisor for process management
sudo apt install supervisor -y
```

#### 3.7 Configure Supervisor
Create `/etc/supervisor/conf.d/flexa-backend.conf`:
```ini
[program:flexa-backend]
directory=/home/ubuntu/flexa-chatbot/flexa-backendnew-main
command=/home/ubuntu/flexa-chatbot/flexa-backendnew-main/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 5000
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/flexa-backend.err.log
stdout_logfile=/var/log/flexa-backend.out.log
```

Start service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start flexa-backend
```

#### 3.8 Configure Nginx
Create `/etc/nginx/sites-available/flexa-backend`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/flexa-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Cost:** ~$5-10/month for t2.micro + S3/CloudFront

---

## Option 4: DigitalOcean

### Using App Platform

#### 4.1 Create Account
1. Sign up at https://digitalocean.com
2. Add payment method

#### 4.2 Create App
1. Click **"Create"** → **"Apps"**
2. Connect GitHub repository
3. Select `flexa-chatbot` repo

#### 4.3 Configure Components

**Backend Component:**
- Type: **Web Service**
- Source Directory: `flexa-backendnew-main`
- Build Command: `pip install -r requirements.txt`
- Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
- HTTP Port: `8080`
- Instance Size: **Basic ($5/mo)**

**Frontend Component:**
- Type: **Static Site**
- Source Directory: `flexa-frontend-main`
- Build Command: `npm run build`
- Output Directory: `build`

#### 4.4 Environment Variables
Add to backend component:
- `PYTHON_VERSION`: `3.10`

#### 4.5 Deploy
Click **"Create Resources"** and wait for deployment.

**Cost:** $10/month ($5 frontend + $5 backend)

---

## Option 5: Docker

### Create Docker Files

#### Backend Dockerfile
Create `flexa-backendnew-main/Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
```

#### Frontend Dockerfile
Create `flexa-frontend-main/Dockerfile`:
```dockerfile
# Build stage
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Nginx Configuration
Create `flexa-frontend-main/nginx.conf`:
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Docker Compose

Create `docker-compose.yml` in root:
```yaml
version: '3.8'

services:
  backend:
    build: ./flexa-backendnew-main
    ports:
      - "5000:5000"
    environment:
      - PORT=5000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./flexa-frontend-main
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    environment:
      - REACT_APP_API_URL=http://localhost:5000
```

### Deploy with Docker

#### Local Testing
```bash
docker-compose up --build
```

#### Deploy to Cloud

**Google Cloud Run:**
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/flexa-backend flexa-backendnew-main
gcloud builds submit --tag gcr.io/PROJECT_ID/flexa-frontend flexa-frontend-main

# Deploy
gcloud run deploy flexa-backend --image gcr.io/PROJECT_ID/flexa-backend --platform managed
gcloud run deploy flexa-frontend --image gcr.io/PROJECT_ID/flexa-frontend --platform managed
```

**AWS ECS:**
```bash
# Create ECR repositories
aws ecr create-repository --repository-name flexa-backend
aws ecr create-repository --repository-name flexa-frontend

# Build and push
docker build -t flexa-backend flexa-backendnew-main
docker tag flexa-backend:latest YOUR_ECR_URI/flexa-backend:latest
docker push YOUR_ECR_URI/flexa-backend:latest

# Create ECS task and service
# (Use AWS Console or CLI)
```

---

## Environment Configuration

### Frontend Environment Variables

Create `.env.production` in `flexa-frontend-main/`:
```env
REACT_APP_API_URL=https://your-backend-url.com
REACT_APP_ENVIRONMENT=production
```

Update `src/pages/Chat.js`:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const ENV = process.env.REACT_APP_ENVIRONMENT || 'development';

// Use in fetch calls
const startChat = async () => {
  const response = await fetch(`${API_URL}/chat/start`);
  // ...
};
```

### Backend Environment Variables

For production, set in deployment platform:
```env
PORT=5000
PYTHON_VERSION=3.10.0
CORS_ORIGINS=https://your-frontend-url.com
```

Update `main.py` to use environment variables:
```python
import os
from fastapi.middleware.cors import CORSMiddleware

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Domain Setup

### Custom Domain on Vercel

1. Go to Vercel Dashboard → Your Project
2. Click **"Settings"** → **"Domains"**
3. Add your domain: `flexa.yourdomain.com`
4. Update DNS records as instructed by Vercel:
   ```
   Type: CNAME
   Name: flexa
   Value: cname.vercel-dns.com
   ```

### Custom Domain on Render

1. Go to Render Dashboard → Your Service
2. Click **"Settings"** → **"Custom Domains"**
3. Add domain: `api.yourdomain.com`
4. Update DNS records:
   ```
   Type: CNAME
   Name: api
   Value: your-service.onrender.com
   ```

### SSL/HTTPS

- ✅ Vercel: Automatic SSL
- ✅ Render: Automatic SSL
- ✅ Heroku: Automatic SSL
- ⚠️ AWS EC2: Use Let's Encrypt (certbot)

#### Setup SSL on EC2:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## Monitoring

### Free Monitoring Tools

#### 1. UptimeRobot (Uptime Monitoring)
1. Sign up at https://uptimerobot.com
2. Add monitors for:
   - Frontend: `https://flexa-frontend.vercel.app`
   - Backend: `https://flexa-backend.onrender.com/docs`
3. Set alert contacts (email/SMS)

#### 2. Sentry (Error Tracking)

**Install:**
```bash
npm install --save @sentry/react
```

**Configure in `src/index.js`:**
```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: process.env.REACT_APP_ENVIRONMENT,
  tracesSampleRate: 1.0,
});
```

**Backend (add to requirements.txt):**
```
sentry-sdk[fastapi]==1.40.0
```

**Configure in `main.py`:**
```python
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    environment="production",
)
```

#### 3. Google Analytics

Add to `public/index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

#### 4. Backend Health Check

Add to `main.py`:
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

Monitor with:
```bash
curl https://your-backend-url.com/health
```

---

## CI/CD (Continuous Integration/Deployment)

### GitHub Actions

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Vercel CLI
        run: npm i -g vercel
      
      - name: Deploy to Vercel
        run: |
          cd flexa-frontend-main
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }} --yes
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

**Setup Secrets:**
1. Go to GitHub repo → Settings → Secrets
2. Add:
   - `RENDER_DEPLOY_HOOK`: From Render service settings
   - `VERCEL_TOKEN`: From Vercel account settings
   - `VERCEL_ORG_ID`: From `.vercel/project.json`
   - `VERCEL_PROJECT_ID`: From `.vercel/project.json`

---

## Troubleshooting

### Common Issues

#### 1. CORS Errors
**Problem:** Frontend can't access backend API

**Solution:**
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. 404 on React Routes
**Problem:** Refresh on `/chat` gives 404

**Solutions:**

**Vercel:** Create `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

**Nginx:**
```nginx
location / {
    try_files $uri /index.html;
}
```

#### 3. Backend Slow/Timeout
**Problem:** First request takes too long

**Causes:**
- Render free tier sleeps after 15 min inactivity
- Large ML model loading

**Solutions:**
- Upgrade to paid tier ($7/mo - always on)
- Add loading indicator in frontend
- Use external ping service to keep awake
- Optimize model loading (lazy load)

#### 4. Build Failures

**Frontend Build Fails:**
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Backend Build Fails:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 5. Model File Too Large

**Problem:** Git won't push large `.joblib` file

**Solution:** Use Git LFS
```bash
git lfs install
git lfs track "*.joblib"
git add .gitattributes
git commit -m "Track joblib files with Git LFS"
```

Or download model on startup:
```python
# Download from S3/cloud storage on first run
if not os.path.exists("models/flexa_plan_model.joblib"):
    download_model_from_cloud()
```

#### 6. Environment Variables Not Working

**Check:**
1. Variable names correct
2. `.env` files in correct location
3. Restart development server
4. In production, set in platform dashboard

**Debug:**
```javascript
console.log('API URL:', process.env.REACT_APP_API_URL);
```

---

## Security Checklist

Before going live:

- ✅ **HTTPS Enabled** (automatic on Vercel/Render)
- ✅ **CORS Configured** (specific domains only)
- ✅ **Rate Limiting** (prevent abuse)
- ✅ **Input Validation** (sanitize user inputs)
- ✅ **Environment Variables** (no secrets in code)
- ✅ **Dependencies Updated** (no known vulnerabilities)
- ✅ **Error Handling** (don't expose stack traces)
- ✅ **Backup Strategy** (for any data)

### Add Rate Limiting

Backend (`main.py`):
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat/message")
@limiter.limit("10/minute")  # 10 requests per minute
async def chat_message(request: Request, payload: ChatMessageRequest):
    # ... existing code
```

Add to `requirements.txt`:
```
slowapi==0.1.9
```

---

## Performance Optimization

### Frontend

#### 1. Code Splitting
```javascript
// Lazy load Chat component
const Chat = lazy(() => import('./pages/Chat'));

<Suspense fallback={<div>Loading...</div>}>
  <Routes>
    <Route path="/chat" element={<Chat />} />
  </Routes>
</Suspense>
```

#### 2. Image Optimization
- Use WebP format
- Lazy load images
- Compress images (TinyPNG)

#### 3. Caching
Add to `public/index.html`:
```html
<meta http-equiv="Cache-Control" content="max-age=31536000" />
```

### Backend

#### 1. Response Caching
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@app.get("/workouts")
@cache(expire=3600)  # Cache for 1 hour
async def get_workouts():
    return workouts_data
```

#### 2. Database Connection Pooling
If using database:
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

#### 3. Async Operations
```python
import asyncio

@app.post("/recommend")
async def get_recommendation(profile: dict):
    # Use async for I/O operations
    result = await asyncio.to_thread(
        recommender.recommend, profile
    )
    return result
```

---

## Maintenance Tasks

### Weekly
- ✅ Check error logs (Sentry)
- ✅ Monitor uptime (UptimeRobot)
- ✅ Review analytics (Google Analytics)

### Monthly
- ✅ Update dependencies
- ✅ Review and optimize performance
- ✅ Check security vulnerabilities
- ✅ Backup data/models

### Update Dependencies

**Frontend:**
```bash
npm outdated
npm update
npm audit fix
```

**Backend:**
```bash
pip list --outdated
pip install -U package-name
```

---

## Scaling Considerations

### When to Scale?

- 🚨 Response time > 3 seconds
- 🚨 Server errors increasing
- 🚨 Concurrent users > 100
- 🚨 CPU/Memory usage > 80%

### Scaling Options

#### Vertical Scaling (Upgrade Instance)
- Render: $7/mo → $25/mo (better CPU/RAM)
- AWS: t2.micro → t2.small → t2.medium

#### Horizontal Scaling (Multiple Instances)
- Load balancer + multiple backend instances
- CDN for frontend (CloudFront, Cloudflare)

#### Database Optimization
- Add caching layer (Redis)
- Use connection pooling
- Index frequently queried fields

#### ML Model Optimization
- Load model once at startup (not per request)
- Use model quantization
- Consider model serving (TensorFlow Serving, Seldon)

---

## Backup Strategy

### Code Backup
- ✅ GitHub (already done)
- ✅ Regular commits
- ✅ Tagged releases

### ML Model Backup
Upload to cloud storage:

**AWS S3:**
```bash
aws s3 cp models/flexa_plan_model.joblib s3://your-bucket/models/
```

**Google Cloud Storage:**
```bash
gsutil cp models/flexa_plan_model.joblib gs://your-bucket/models/
```

**Download on startup:**
```python
import boto3
import os

def download_model():
    if not os.path.exists("models/flexa_plan_model.joblib"):
        s3 = boto3.client('s3')
        s3.download_file(
            'your-bucket', 
            'models/flexa_plan_model.joblib',
            'models/flexa_plan_model.joblib'
        )

# Call on app startup
download_model()
```

---

## Cost Optimization Tips

1. **Use Free Tiers**
   - Start with Vercel + Render free tiers
   - Upgrade only when needed

2. **Optimize Images**
   - Compress all images
   - Use CDN (free on Vercel)

3. **Monitor Usage**
   - Set up billing alerts
   - Review monthly costs

4. **Cache Aggressively**
   - Cache static content
   - Cache API responses (when appropriate)

5. **Use Serverless for Spiky Traffic**
   - Only pay for actual usage
   - Auto-scales down to zero

---

## Final Deployment Checklist

### Before Launch
- [ ] All features tested locally
- [ ] Backend API endpoints work
- [ ] Frontend connects to backend
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] SSL/HTTPS enabled
- [ ] Custom domain configured (optional)
- [ ] Error tracking setup (Sentry)
- [ ] Analytics setup (Google Analytics)
- [ ] Uptime monitoring (UptimeRobot)
- [ ] README updated
- [ ] DEPLOYMENT_GUIDE.md reviewed

### After Launch
- [ ] Test complete user flow
- [ ] Check all pages load
- [ ] Verify API calls work
- [ ] Test on mobile devices
- [ ] Check browser console for errors
- [ ] Monitor first few users
- [ ] Set up alerts
- [ ] Share with testers
- [ ] Collect feedback
- [ ] Plan updates

---

## Support & Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com
- **React**: https://react.dev
- **Vercel**: https://vercel.com/docs
- **Render**: https://render.com/docs
- **Heroku**: https://devcenter.heroku.com
- **AWS**: https://docs.aws.amazon.com
- **DigitalOcean**: https://docs.digitalocean.com

### Communities
- **FastAPI Discord**: https://discord.gg/fastapi
- **React Community**: https://react.dev/community
- **Stack Overflow**: Tag questions appropriately

### Getting Help
1. Check error logs first
2. Search documentation
3. Search Stack Overflow
4. Ask in relevant Discord/Slack
5. Create GitHub issue (for libraries)

---

## Conclusion

**Recommended Path for Beginners:**
1. ✅ Deploy Backend to Render (10 min)
2. ✅ Deploy Frontend to Vercel (10 min)
3. ✅ Test thoroughly (15 min)
4. ✅ Set up monitoring (10 min)
5. ✅ Add custom domain (optional, 15 min)

**Total Time:** ~45-60 minutes

**Total Cost:** $0/month (with limitations)

**When to Upgrade:**
- More than 100 daily users → $7-14/month
- Need 24/7 uptime → $14-25/month
- High traffic/performance → $50-100+/month

---

## Next Steps

1. Choose your deployment platform
2. Follow the relevant section above
3. Deploy backend first (get API URL)
4. Update frontend with backend URL
5. Deploy frontend
6. Test everything
7. Set up monitoring
8. Invite users
9. Iterate based on feedback
10. Scale as needed

**Good luck with your deployment! 🚀**

---

*Last Updated: January 22, 2026*  
*Flexa AI Chatbot - Deployment Guide v1.0*
