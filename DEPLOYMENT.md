Deployment Guide
Prerequisites
Railway account (Backend)
Vercel account (Frontend)
GitHub repository
Backend Deployment (Railway)
Create new project on Railway
Connect GitHub repository
Select backend as root directory
Add environment variables:
DATABASE_URL
SECRET_KEY
CORS_ORIGINS
Railway will auto-detect Python and install dependencies
Add PostgreSQL service and link it
Frontend Deployment (Vercel)
Import project from GitHub
Set root directory to frontend
Build command: npm run build
Output directory: dist
Add environment variable:
VITE_API_URL (your Railway backend URL)
Database Migration
Run migrations on Railway:
railway run alembic upgrade head
Health Checks
Backend: https://your-backend.railway.app/health
Frontend: Your Vercel URL
