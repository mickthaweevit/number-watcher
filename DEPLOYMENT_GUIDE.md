# NumWatch - Production Deployment Guide

## 🚀 Deployment Architecture

### Services
- **Database**: Supabase PostgreSQL (Free tier)
- **Backend**: Render Web Service (Free tier) 
- **Frontend**: Render Static Site (Free tier)
- **Domain**: Custom domain with SSL

## 📋 Step-by-Step Deployment

### Step 1: Database Setup (Supabase)

1. **Create Supabase Account**
   - Go to [supabase.com](https://supabase.com)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Name: `numwatch-db`
   - Generate secure password
   - Choose region closest to you

3. **Get Database URL**
   - Go to Settings → Database
   - Copy connection string:
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
   ```

4. **Run Database Migrations**
   - Tables will be created automatically on first backend startup

### Step 2: Backend Deployment (Render)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select `number-watcher` repo

3. **Configure Service**
   ```
   Name: numwatch-backend
   Environment: Python 3
   Build Command: cd backend && pip install -r requirements.txt
   Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Root Directory: backend
   Python Version: 3.11.9
   ```

4. **Set Environment Variables**
   ```
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
   JWT_SECRET_KEY=[Generate 32+ character random string]
   CORS_ORIGINS=https://numwatch-frontend.onrender.com
   ENVIRONMENT=production
   DEBUG=false
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note your backend URL: `https://numwatch-backend.onrender.com`

### Step 3: Frontend Deployment (Render)

1. **Create Static Site**
   - Click "New" → "Static Site"
   - Connect same GitHub repository

2. **Configure Static Site**
   ```
   Name: numwatch-frontend
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   ```

3. **Set Environment Variables**
   ```
   VITE_API_URL=https://numwatch-backend.onrender.com
   ```

4. **Deploy**
   - Click "Create Static Site"
   - Wait for deployment (3-5 minutes)
   - Note your frontend URL: `https://numwatch-frontend.onrender.com`

### Step 4: Create Production Admin

1. **Access Backend Console**
   - Go to Render dashboard → numwatch-backend
   - Click "Shell" tab
   - Run: `python create_production_admin.py`

2. **Save Admin Credentials**
   - Copy the generated username/password
   - Store securely (password won't be shown again)

### Step 5: Test Deployment

1. **Test Backend API**
   ```bash
   curl https://numwatch-backend.onrender.com/health
   ```

2. **Test Frontend**
   - Visit: `https://numwatch-frontend.onrender.com`
   - Login with admin credentials
   - Test all functionality

3. **Import Sample Data**
   ```bash
   curl -X POST https://numwatch-backend.onrender.com/import-sample-data
   ```

## 🔧 Production Configuration

### Environment Variables

#### Backend (.env.production)
```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here
CORS_ORIGINS=https://numwatch-frontend.onrender.com
ENVIRONMENT=production
DEBUG=false
```

#### Frontend (.env.production)
```bash
VITE_API_URL=https://numwatch-backend.onrender.com
```

## 🌐 Custom Domain (Optional)

### Step 1: Purchase Domain
- Buy domain from Namecheap, GoDaddy, etc.
- Example: `numwatch.app`

### Step 2: Configure DNS
- Add CNAME record: `www` → `numwatch-frontend.onrender.com`
- Add A record: `@` → Render's IP

### Step 3: Update Render Settings
- Go to numwatch-frontend settings
- Add custom domain: `numwatch.app`
- SSL certificate will be auto-generated

### Step 4: Update CORS
- Update backend CORS_ORIGINS: `https://numwatch.app,https://www.numwatch.app`

## 🔒 Security Checklist

- ✅ Strong JWT secret key (32+ characters)
- ✅ Secure database password
- ✅ HTTPS enabled (automatic with Render)
- ✅ CORS properly configured
- ✅ Admin credentials saved securely
- ✅ Environment variables not in code

## 📊 Monitoring

### Render Dashboard
- Monitor service health
- View deployment logs
- Check resource usage

### Supabase Dashboard
- Monitor database performance
- View query logs
- Check storage usage

## 🚨 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check environment variables
   - Verify database connection
   - Check build logs

2. **Frontend can't connect to backend**
   - Verify VITE_API_URL is correct
   - Check CORS configuration
   - Ensure backend is running

3. **Database connection failed**
   - Verify DATABASE_URL format
   - Check Supabase project status
   - Confirm password is correct

### Useful Commands

```bash
# Check backend health
curl https://your-backend.onrender.com/health

# View backend logs
# Go to Render dashboard → Service → Logs

# Test database connection
# Go to Supabase → SQL Editor → Run: SELECT 1;
```

## 💰 Cost Breakdown

### Free Tier Limits
- **Render**: 750 hours/month (enough for 1 service)
- **Supabase**: 500MB database, 2GB bandwidth
- **Total Cost**: $0/month

### Paid Upgrades (Optional)
- **Render Pro**: $7/month (no sleep, better performance)
- **Supabase Pro**: $25/month (8GB database, more features)

## 🎯 Next Steps After Deployment

1. **Share your app** with friends/colleagues
2. **Gather feedback** from real users
3. **Monitor performance** and usage
4. **Plan Phase 8** features (charts, exports, etc.)
5. **Add to portfolio** as production project

---

**Congratulations! Your NumWatch application is now live in production! 🎉**