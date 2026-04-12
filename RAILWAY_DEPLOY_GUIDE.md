# Railway Backend Deployment Guide

## Quick Deploy (5 Minutes)

### Step 1: Go to Railway
1. Visit: **https://railway.app/**
2. Click **"Start a New Project"**
3. Sign in with GitHub (recommended)

### Step 2: Deploy from Local Folder
1. Click **"Deploy from GitHub repo"**
2. OR click **"Empty Project"** then:
   - Click **"+ New"**
   - Select **"Empty Service"**
   - Click **"Settings"** tab
   - Scroll to **"Source"**
   - Click **"Connect Repo"** (you'll need to push to GitHub first)

### Alternative: Direct Deploy via CLI (If you prefer)
```bash
# In your backend folder
cd backend
railway login --browserless
# Follow the token instructions
railway init
railway up
```

### Step 3: Configure Environment Variables
In Railway dashboard, go to your service → **Variables** tab:

**Required Variables:**
```
ALLOWED_ORIGINS=https://gcfb-ops-dashboard.vercel.app
```

**Optional (if you add a database later):**
```
DATABASE_URL=your_postgres_url
```

### Step 4: Get Your Backend URL
1. Go to **Settings** tab in Railway
2. Under **Networking** → Click **"Generate Domain"**
3. Copy the URL (will be like: `https://your-app.up.railway.app`)

### Step 5: Update Frontend to Use Railway Backend
Once you have the Railway URL, update your Vercel deployment:

```bash
# Set the environment variable in Vercel
vercel env add VITE_API_URL
# Enter: https://your-app.up.railway.app/api
# Select: Production
```

Then redeploy:
```bash
vercel --prod
```

## Files Already Created for Railway

All necessary files are ready in your `backend` folder:
- `requirements.txt` - Python dependencies
- `Procfile` - Start command
- `runtime.txt` - Python version
- `railway.json` - Railway configuration

## Easier Option: Use Railway's GitHub Integration

1. **Push your backend to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/gcfb-backend.git
   git push -u origin main
   ```

2. **Deploy from Railway:**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `backend` folder as root directory
   - Railway will auto-detect Python and deploy!

## Expected Result

Once deployed:
- Backend URL: `https://your-app.up.railway.app`
- API endpoints: `https://your-app.up.railway.app/api/...`
- Frontend: `https://gcfb-ops-dashboard.vercel.app`

## Test Your Deployment

Visit: `https://your-app.up.railway.app/docs`
You should see the FastAPI Swagger documentation!

## Next Steps After Backend Deployment

1. Get your Railway backend URL
2. Update Vercel environment variable
3. Redeploy frontend
4. Test the full application!
