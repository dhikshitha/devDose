# DevDose Deployment Checklist for Render

## Pre-Deployment Checklist

- [ ] Ensure all code is committed and pushed to GitHub
- [ ] Verify `backend/requirements.txt` exists and includes gunicorn
- [ ] Verify `backend/Procfile` exists with content: `web: gunicorn app:app`
- [ ] Verify `frontend/public/_redirects` exists for React Router
- [ ] Verify `frontend/.env.production` exists (will update URL after deployment)

## Step-by-Step Deployment Process

### 1. Create PostgreSQL Database on Render

- [ ] Log in to [Render Dashboard](https://dashboard.render.com)
- [ ] Click "New +" → "PostgreSQL"
- [ ] Configure:
  - Name: `devdose-db`
  - Database: `devdose`
  - User: `devdose`
  - Region: Oregon (US West)
  - PostgreSQL Version: 15
  - Plan: Free
- [ ] Click "Create Database"
- [ ] Wait for creation (5-10 minutes)
- [ ] Copy the "External Database URL" (starts with `postgres://`)

### 2. Deploy Backend

- [ ] Click "New +" → "Web Service"
- [ ] Select your GitHub repository
- [ ] Configure:
  - Name: `devdose-backend`
  - Region: Oregon (US West) - same as database
  - Branch: `main` or `master`
  - Root Directory: `backend`
  - Runtime: Python 3
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn app:app`
  - Plan: Free
- [ ] Add Environment Variables:
  ```
  DATABASE_URL=<paste-external-database-url-from-step-1>
  FLASK_ENV=production
  JWT_SECRET_KEY=<generate-secure-key>
  NEWS_API_KEY=<your-newsapi-key>
  CORS_ORIGINS=https://devdose-frontend.onrender.com
  ```
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (5-10 minutes)
- [ ] Note your backend URL (e.g., `https://devdose-backend.onrender.com`)

### 3. Initialize Database

- [ ] Go to your backend service in Render
- [ ] Click "Shell" tab
- [ ] Run:
  ```bash
  python
  from app import create_app, db
  app = create_app()
  with app.app_context():
      db.create_all()
      print("Tables created!")
  exit()
  ```
- [ ] Run seed scripts:
  ```bash
  python seed_data.py
  python seed_challenges.py
  ```

### 4. Deploy Frontend

- [ ] Update `frontend/.env.production` with your backend URL:
  ```
  REACT_APP_API_URL=https://devdose-backend.onrender.com/api
  ```
- [ ] Commit and push this change
- [ ] In Render, click "New +" → "Static Site"
- [ ] Select your GitHub repository
- [ ] Configure:
  - Name: `devdose-frontend`
  - Branch: `main` or `master`
  - Root Directory: `frontend`
  - Build Command: `npm install && npm run build`
  - Publish Directory: `build`
  - Plan: Free
- [ ] Click "Create Static Site"
- [ ] Wait for deployment (5-10 minutes)
- [ ] Note your frontend URL (e.g., `https://devdose-frontend.onrender.com`)

### 5. Update Backend CORS

- [ ] Go to your backend service
- [ ] Update CORS_ORIGINS environment variable to your actual frontend URL
- [ ] Service will auto-redeploy

### 6. Test Deployment

- [ ] Visit your frontend URL
- [ ] Test signup flow
- [ ] Test login
- [ ] Verify concepts load
- [ ] Test challenges
- [ ] Check all features

## Environment Variables Reference

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@host/dbname
FLASK_ENV=production
JWT_SECRET_KEY=your-secure-key-here
NEWS_API_KEY=your-newsapi-key
CORS_ORIGINS=https://devdose-frontend.onrender.com
```

### Frontend (.env.production)
```
REACT_APP_API_URL=https://devdose-backend.onrender.com/api
```

## Common Issues and Solutions

### Issue: Database connection failed
- Check DATABASE_URL starts with `postgresql://` not `postgres://`
- Verify database and backend are in same region

### Issue: CORS errors
- Ensure CORS_ORIGINS matches your frontend URL exactly
- No trailing slash in CORS_ORIGINS
- Clear browser cache

### Issue: Frontend shows blank page
- Check browser console for errors
- Verify API URL is correct in .env.production
- Ensure _redirects file exists

### Issue: Backend crashes on startup
- Check Render logs for specific error
- Verify all dependencies in requirements.txt
- Check Procfile location and content

## Post-Deployment

- [ ] Monitor service logs for errors
- [ ] Test all features thoroughly
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring/alerts
- [ ] Document API endpoints
- [ ] Create backup strategy

## Useful Commands

Generate secure JWT key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Test backend health:
```bash
curl https://devdose-backend.onrender.com/api/health
```

## Support Resources

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [PostgreSQL on Render](https://render.com/docs/databases)
- [Deploy Flask on Render](https://render.com/docs/deploy-flask)