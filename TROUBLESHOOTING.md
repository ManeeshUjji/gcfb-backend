# Troubleshooting Guide

## Issue: "Failed to load forecast data"

### Problem
The forecast API endpoint is taking 50+ seconds to respond on the first load, which exceeds the default timeout.

### Solutions Implemented
1. ✅ **Increased timeout to 60 seconds** in `frontend/src/utils/api.js`
2. ✅ **Added better error messages** to indicate long loading times are expected
3. ✅ **Updated CORS settings** to allow both localhost:3000 and localhost:5173
4. ✅ **Improved loading indicator** with time expectations

### Why It's Slow
The forecast endpoint:
- Makes ML predictions for all 60 partner sites
- Queries weather data for each site
- Performs database lookups
- This is normal for POC; production would use caching

### How to Fix
1. **Wait longer**: First load takes 50-60 seconds, subsequent loads are faster
2. **Reload the page**: After the first successful load, data may be cached
3. **Check backend logs**: Verify the API is processing requests

---

## Issue: Backend Connection Errors

### Symptoms
- "Failed to load forecast data"
- "Failed to generate dispatch plan"
- "Failed to load expiring items"

### Checklist

#### 1. Is the backend running?
```powershell
netstat -ano | findstr :8000
```
Should show: `LISTENING       [PID]`

If not running:
```powershell
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Is the frontend running?
```powershell
netstat -ano | findstr :3000
```

If not running:
```powershell
cd frontend
npm run dev
```

#### 3. Check backend health
Open: http://localhost:8000/health

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "ml_model_loaded": true,
  "timestamp": "..."
}
```

#### 4. Check API docs
Open: http://localhost:8000/docs

Should show Swagger UI with all endpoints.

#### 5. Test API directly
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/sites" -Method GET
```

Should return JSON with partner sites.

#### 6. Check CORS settings
In `backend/.env`:
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### 7. Check frontend API URL
In `frontend/.env`:
```
VITE_API_URL=http://localhost:8000/api
```

#### 8. Clear browser cache
- Press Ctrl+Shift+R (hard reload)
- Or open DevTools > Network tab > Disable cache

---

## Issue: "Failed to generate dispatch plan"

### Possible Causes
1. **No active trucks**: Check database has trucks with status='active'
2. **Invalid input**: Truck count must be >= 1
3. **OR-Tools timeout**: Optimization taking too long (> 10 seconds)
4. **Backend error**: Check backend terminal for errors

### Solutions
1. **Verify truck data**:
   ```sql
   SELECT * FROM truck_fleet WHERE status = 'active';
   ```
   Should return 5 trucks.

2. **Check backend logs**: Look for error messages in backend terminal

3. **Reduce truck count**: Try with 1-2 trucks first

4. **Check backend response**:
   Open DevTools > Network tab
   Look for `/api/dispatch` request
   Check response status and error message

---

## Issue: "Failed to load expiring items"

### Possible Causes
1. **No expiring items**: Database has no items expiring within 72 hours
2. **Database connection error**: SQLite file locked or missing
3. **Backend error**: Check backend terminal for errors

### Solutions
1. **Verify inventory data**:
   ```sql
   SELECT * FROM warehouse_inventory 
   WHERE expiration_date <= date('now', '+3 days');
   ```
   Should return 3-5 items.

2. **Re-seed database**: If no items exist
   ```powershell
   cd backend
   python data/seed.py
   ```

3. **Check database file**: Verify `backend/gcfb_dev.db` exists

---

## Issue: Map Not Loading

### Possible Causes
1. **GeoJSON file missing**: `frontend/public/ohio_zips.geojson`
2. **Leaflet CSS not loading**: Check network tab for 404s
3. **Invalid GeoJSON**: Syntax error in JSON file

### Solutions
1. **Verify GeoJSON exists**:
   ```powershell
   Test-Path "frontend\public\ohio_zips.geojson"
   ```
   Should return `True`.

2. **Check browser console**: Look for JavaScript errors

3. **Verify Leaflet CSS**: Check `frontend/index.html` has:
   ```html
   <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
   ```

---

## Performance Issues

### Forecast API Slow (50+ seconds)
**This is expected** on first load. Subsequent loads should be faster.

**Optimizations for production:**
- Implement Redis caching for predictions
- Pre-compute forecasts on schedule
- Use faster ML inference (ONNX Runtime)
- Parallelize site predictions
- Add database query optimization

### Dispatch Optimization Slow (> 10 seconds)
**This is normal** for OR-Tools vehicle routing.

**Expected times:**
- 3 trucks, 30 sites: ~5 seconds
- 5 trucks, 50 sites: ~10 seconds

**If taking longer:**
- Reduce number of sites in optimization
- Adjust OR-Tools time limit in `routers/dispatch.py`

---

## Browser Console Errors

### CORS Error
```
Access to XMLHttpRequest at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
1. Update `backend/.env`:
   ```
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   ```
2. Restart backend server

### Network Error
```
AxiosError: Network Error
```

**Solution:**
1. Backend not running - start backend server
2. Wrong API URL - check `frontend/.env`
3. Firewall blocking - allow port 8000

---

## Testing Checklist

After making changes, test:
- [ ] Backend health: http://localhost:8000/health
- [ ] API docs: http://localhost:8000/docs
- [ ] Frontend loads: http://localhost:3000
- [ ] Map displays with colored ZIPs
- [ ] Forecast data loads (wait 60 seconds)
- [ ] Dispatch plan generates
- [ ] Expiration alerts load
- [ ] No errors in browser console
- [ ] No errors in backend terminal

---

## Quick Reset

If all else fails:

```powershell
# Stop all servers (Ctrl+C in each terminal)

# Backend
cd backend
python data/seed.py  # Re-seed database
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (in new terminal)
cd frontend
npm run dev

# Wait 60 seconds for first forecast load
# Then test all modules
```

---

## Getting Help

1. **Check terminal output**: Backend and frontend logs
2. **Check browser DevTools**: Console and Network tabs
3. **Review error messages**: Often indicate the issue
4. **Check this guide**: Common issues and solutions above
5. **Refer to documentation**:
   - `README.md` - Setup instructions
   - `TEST_SCENARIOS.md` - Test cases
   - `QUICK_START.md` - Running the app

---

**Last Updated:** April 10, 2026
