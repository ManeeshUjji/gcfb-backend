# Quick Start Guide - GCFB Dashboard

## Current Status
✅ **Milestones 6-9 COMPLETE** - Application is fully functional and ready for demo

---

## Running the Application

### Backend Server
```powershell
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
**Status:** Currently running on http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### Frontend Server
```powershell
cd frontend
npm run dev
```
**Status:** Currently running on http://localhost:3000  
**Access:** Open browser to http://localhost:3000

---

## Application Features

### Module 1: Demand Heatmap (`/`)
- View color-coded ZIP demand forecast (green/yellow/red)
- Toggle between Today, Tomorrow, and This Week
- Click any ZIP to see detailed forecast
- View partner sites on map
- See top contributing factors for demand

### Module 2: Dispatch Planner (`/dispatch`)
- Set truck count and volunteer count
- Generate optimized delivery routes
- View routes on map (color-coded by truck)
- See text plan with stops and distances
- Print/export functionality

### Module 3: Expiration Alerts (`/alerts`)
- View items expiring within 72 hours
- Color-coded urgency (red < 24hrs, orange < 72hrs)
- Find top 3 suggested sites for each item
- Assign items to sites with one click
- Assignments automatically added to dispatch plan

---

## Testing the Demo Flow

1. **Start on Heatmap** (http://localhost:3000)
   - Map loads with colored ZIP codes
   - Click any red or yellow ZIP
   - Review forecast details in side panel

2. **Check Expiration Alerts** (http://localhost:3000/alerts)
   - View expiring items list
   - Click "Find Sites" for an item
   - Click "Assign" for top suggested site
   - See success notification

3. **Generate Dispatch Plan** (http://localhost:3000/dispatch)
   - See your assignment listed
   - Set trucks to 3, volunteers to 100
   - Click "Generate Today's Plan"
   - Wait ~10 seconds for optimization
   - View routes on map
   - Review text plan details

---

## API Endpoints (Backend)

### Forecast
- `GET /api/forecast?date=today` - Get all ZIP forecasts
- `GET /api/forecast/{zip_code}?date=today` - Get detailed forecast

### Sites
- `GET /api/sites` - Get all partner sites
- `GET /api/sites/{zip_code}` - Get sites by ZIP

### Dispatch
- `POST /api/dispatch` - Generate optimized routes
- `POST /api/dispatch/assign` - Assign item to site

### Inventory
- `GET /api/inventory/expiring` - Get expiring items (72 hrs)
- `GET /api/inventory/expiring/{item_id}/sites` - Get suggested sites

---

## Key Files

### Frontend
- `src/App.jsx` - Main app with routing
- `src/context/AppContext.jsx` - Global state management
- `src/components/Map.jsx` - Leaflet map component
- `src/components/DateToggle.jsx` - Date selector
- `src/components/ZipSidePanel.jsx` - ZIP forecast details
- `src/components/DispatchPlanner.jsx` - Route planner UI
- `src/components/ExpirationFeed.jsx` - Expiration alerts
- `src/utils/api.js` - API client

### Backend
- `main.py` - FastAPI application
- `routers/forecast.py` - Forecast endpoints
- `routers/sites.py` - Sites endpoints
- `routers/dispatch.py` - Dispatch endpoints
- `routers/inventory.py` - Inventory endpoints
- `db.py` - Database models
- `schemas.py` - Pydantic schemas

---

## Database

**Location:** `backend/gcfb_dev.db` (SQLite)

**Tables:**
- `partner_sites` - 60 sites across 6 counties
- `historical_distribution` - 90 days of historical data
- `warehouse_inventory` - 15-25 items (3-5 expiring soon)
- `truck_fleet` - 5 trucks
- `volunteer_availability` - 90 days of volunteer data

---

## Performance Notes

- **Forecast API:** Takes ~21 seconds (predicts for all sites)
- **Dispatch API:** Takes ~10 seconds (OR-Tools optimization)
- **Sites API:** < 1 second
- **Inventory API:** < 1 second

**Note:** Forecast is slow due to ML predictions for all sites. This is acceptable for POC. Production optimizations would include caching and pre-computation.

---

## Known Issues

1. **Weather API:** Using fallback values (OpenWeatherMap API key not configured)
2. **Forecast Performance:** Slow for large number of sites (acceptable for POC)
3. **Print Layout:** Minor differences in Firefox

---

## Browser Compatibility

✅ Chrome (latest)  
✅ Firefox (latest)  
✅ Edge (latest)

---

## Documentation

- `README.md` - Project overview
- `SETUP.md` - Setup instructions
- `TEST_SCENARIOS.md` - Comprehensive test cases
- `MILESTONES_6-9_COMPLETE.md` - Implementation summary
- `milestones.md` - All project milestones

---

## Next Steps

### Milestone 10: Logging, Monitoring, Documentation & Deployment
- Enhanced logging
- Monitoring setup
- Deploy to hosting platform
- Production deployment guide

---

## Support

For issues or questions:
1. Check backend logs in terminal
2. Check browser console for frontend errors
3. Review API docs at http://localhost:8000/docs
4. Refer to TEST_SCENARIOS.md for test cases

---

**Last Updated:** April 10, 2026  
**Status:** ✅ READY FOR DEMO
