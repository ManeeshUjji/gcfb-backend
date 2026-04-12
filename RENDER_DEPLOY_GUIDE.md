# Render.com Backend Deployment (Easiest Option!)

## Why Render?
- No CLI needed - all via web interface
- Free tier available
- Auto-deploys from GitHub
- Simple setup (3 minutes!)

## Step-by-Step Deployment

### Step 1: Push Backend to GitHub (If not already)

```bash
# Initialize git in your project
git init

# Add all files
git add .

# Commit
git commit -m "Initial GCFB backend"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/gcfb-backend.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. **Go to:** https://render.com/
2. **Sign up/Login** with GitHub
3. Click **"New +"** → **"Web Service"**
4. **Connect your GitHub repository**
5. **Configure the service:**

   ```
   Name: gcfb-backend
   Region: Oregon (US West) or closest to you
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

6. **Select Free tier**
7. Click **"Create Web Service"**

### Step 3: Add Environment Variables

In the Render dashboard:
1. Go to **Environment** tab
2. Add variable:
   - Key: `ALLOWED_ORIGINS`
   - Value: `https://gcfb-ops-dashboard.vercel.app`

### Step 4: Get Your Backend URL

After deployment completes (2-3 minutes):
- Your URL will be: `https://gcfb-backend.onrender.com`
- Test it: `https://gcfb-backend.onrender.com/docs`

### Step 5: Connect Frontend to Backend

Update Vercel to use your new backend:

```bash
# In your project root
vercel env add VITE_API_URL production
# When prompted, enter: https://gcfb-backend.onrender.com/api

# Redeploy frontend
vercel --prod
```

## Alternative: Even Faster with Our Prepared Config

We've created a `render.yaml` file in your backend folder. To use it:

1. Push to GitHub (including the `render.yaml`)
2. On Render, click **"New +"** → **"Blueprint"**
3. Connect your repo
4. Render will auto-configure everything!

## Testing Your Deployment

Once both are deployed:

1. **Backend Health Check:**
   - Visit: `https://gcfb-backend.onrender.com/health`
   - Should return: `{"status": "healthy"}`

2. **API Documentation:**
   - Visit: `https://gcfb-backend.onrender.com/docs`
   - Should show FastAPI Swagger UI

3. **Full Application:**
   - Visit: `https://gcfb-ops-dashboard.vercel.app`
   - Should connect to backend automatically!

## Important Notes

- **First Request:** Render free tier may take 30-60 seconds to wake up on first request
- **Auto-Deploy:** Every push to GitHub will auto-deploy
- **Logs:** Check logs in Render dashboard if issues occur

## Complete URLs

After deployment:
- **Frontend:** https://gcfb-ops-dashboard.vercel.app
- **Backend:** https://gcfb-backend.onrender.com
- **API Docs:** https://gcfb-backend.onrender.com/docs
- **API Endpoints:** https://gcfb-backend.onrender.com/api/...

## Next Steps

1. Push your code to GitHub
2. Deploy on Render (3 minutes)
3. Update Vercel env variable
4. Share your link: **https://gcfb-ops-dashboard.vercel.app**

Done!
