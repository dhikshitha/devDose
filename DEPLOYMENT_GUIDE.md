# DevDose Deployment Guide for Render

This guide will walk you through deploying the DevDose application to Render with PostgreSQL.

## Prerequisites
- A Render account (sign up at https://render.com)
- GitHub repository with your devDose code
- Git installed locally

## Step 1: Prepare Your Code for Deployment

### 1.1 Create a requirements.txt for Backend
First, let's create a requirements.txt file for the backend:

```bash
cd backend
pip freeze > requirements.txt
```

Make sure it includes all necessary packages:
```
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
Flask-JWT-Extended==4.5.2
Flask-Bcrypt==1.0.1
psycopg2-binary==2.9.6
python-dotenv==1.0.0
requests==2.31.0
gunicorn==21.2.0
```

### 1.2 Create a Procfile for Backend
Create a file named `Procfile` in the backend directory:

```
web: gunicorn app:app
```

### 1.3 Update Backend Configuration
Create or update `backend/config.py`:

```python
import os
from datetime import timedelta

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # NewsAPI
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
```

### 1.4 Update app.py to use Config
Update your `backend/app.py`:

```python
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Update CORS configuration
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # ... rest of your code
```

## Step 2: Push Code to GitHub

```bash
# From the root directory
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 3: Create PostgreSQL Database on Render

1. Log in to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Configure your database:
   - **Name**: devdose-db
   - **Database**: devdose
   - **User**: devdose
   - **Region**: Choose closest to you (Oregon is free tier)
   - **PostgreSQL Version**: 15
   - **Plan**: Free (for development)
4. Click "Create Database"
5. Wait for database to be created (takes a few minutes)
6. Once created, copy the "External Database URL" - you'll need this

## Step 4: Deploy Backend to Render

### 4.1 Create Web Service
1. In Render Dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: devdose-backend
   - **Region**: Same as your database
   - **Branch**: main (or master)
   - **Root Directory**: backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### 4.2 Add Environment Variables
Click "Environment" and add:

```
DATABASE_URL=<your-postgres-external-url-from-step-3>
JWT_SECRET_KEY=<generate-a-secure-random-string>
NEWS_API_KEY=<your-newsapi-key>
CORS_ORIGINS=https://devdose-frontend.onrender.com
FLASK_ENV=production
```

To generate a secure JWT secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4.3 Deploy
Click "Create Web Service" and wait for deployment (takes 5-10 minutes)

## Step 5: Initialize Database

Once your backend is deployed:

1. Go to your backend service in Render
2. Click "Shell" tab
3. Run these commands:

```bash
python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Database tables created!")
exit()

# Run seed scripts
python seed_data.py
python seed_challenges.py
```

## Step 6: Deploy Frontend to Render

### 6.1 Create Frontend Configuration
Create `frontend/.env.production`:

```
REACT_APP_API_URL=https://devdose-backend.onrender.com/api
```

### 6.2 Update package.json
Ensure your `frontend/package.json` has:

```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "serve": "serve -s build -l 3000"
  }
}
```

### 6.3 Create Static Site on Render
1. In Render Dashboard, click "New +" → "Static Site"
2. Connect your GitHub repository
3. Configure:
   - **Name**: devdose-frontend
   - **Branch**: main (or master)
   - **Root Directory**: frontend
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: build
   - **Plan**: Free

### 6.4 Add Redirect Rules
Add a `frontend/public/_redirects` file:

```
/* /index.html 200
```

### 6.5 Deploy
Click "Create Static Site" and wait for deployment

## Step 7: Update Backend CORS

Once your frontend is deployed and you have the URL:

1. Go to your backend service in Render
2. Update the CORS_ORIGINS environment variable to include your frontend URL:
   ```
   CORS_ORIGINS=https://devdose-frontend.onrender.com
   ```
3. The service will automatically redeploy

## Step 8: Test Your Deployment

1. Visit your frontend URL: `https://devdose-frontend.onrender.com`
2. Try to sign up a new user
3. Log in and test all features

## Troubleshooting

### Database Connection Issues
- Ensure DATABASE_URL starts with `postgresql://` not `postgres://`
- Check that your database is in the same region as your backend

### CORS Issues
- Verify CORS_ORIGINS includes your frontend URL without trailing slash
- Check browser console for specific CORS errors

### Backend Not Starting
- Check logs in Render dashboard
- Ensure all dependencies are in requirements.txt
- Verify Procfile is in the backend directory

### Frontend Build Fails
- Check that all dependencies are in package.json
- Ensure no hardcoded localhost URLs in code
- Verify environment variables are set

## Monitoring

### View Logs
- Backend: Go to your backend service → "Logs" tab
- Frontend: Go to your static site → "Events" tab
- Database: Go to your database → "Logs" tab

### Check Service Health
- Backend health check: `https://devdose-backend.onrender.com/api/health`
- You can add a health check endpoint:

```python
@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow()})
```

## Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Limited to 750 hours/month across all services
- Database limited to 1GB storage

## Production Considerations

For production deployment:
1. Upgrade to paid plans for better performance
2. Set up custom domain
3. Enable auto-deploy from GitHub
4. Set up monitoring and alerts
5. Configure backup strategy for database
6. Use environment-specific configurations
7. Set up CI/CD pipeline

## Next Steps

1. Configure custom domain (optional)
2. Set up SSL certificates (automatic on Render)
3. Configure monitoring and logging
4. Set up database backups
5. Implement rate limiting
6. Add error tracking (e.g., Sentry)