# Create PostgreSQL database
createdb moveinsync_billing

# Run schema
psql -d moveinsync_billing -f new_schema.sqlfied Billing & Reporting Platform" && \
git branch -M main && \
echo "✅ Git initialized! Now add your GitHub remote with:" && \
echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git" && \
echo "git push -u origin main"
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/moveinsync_billing

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Project
PROJECT_NAME=MoveInSync Billing Platform
VITE_API_URL=http://localhost:8000://YOUR_TOKEN@github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd backend
python -m venv cs
source cs/bin/activate
pip install -r requirements.txt
cd frontend
npm install
cd backend
alembic upg
cd backend
python seed_data.py
python seed_trips.py
cd backend
source cs/bin/activate
uvicorn app.main:app --reload
cd frontend
npm run dev
Production Deployment
See main README.md for deployment instructions.
