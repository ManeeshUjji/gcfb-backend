# GCFB Operational Intelligence Dashboard

A full-stack web application for the Greater Cleveland Food Bank that provides demand forecasting, inventory management, and dispatch planning.

## Features

- **Demand Heatmap**: Visualize demand across ZIP codes with color-coded polygons
- **Expiration Alerts**: Track expiring inventory with intelligent site matching
- **Dispatch Planner**: Generate optimized delivery routes

## Tech Stack

**Frontend:**
- React 18
- Vite
- TailwindCSS
- Leaflet (Maps)
- React Router
- Recharts

**Backend:**
- FastAPI
- Python 3.11
- scikit-learn (ML forecasting)
- OR-Tools (Route optimization)

## Deployment

- Frontend: Vercel
- Backend: Render.com
- Live URL: https://gcfb-ops-dashboard.vercel.app

## Local Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Documentation

- `RENDER_DEPLOY_GUIDE.md` - Backend deployment instructions
- `RAILWAY_DEPLOY_GUIDE.md` - Alternative backend deployment
- `README_TEST_NOW.md` - Testing guide
- `milestones.md` - Project milestones and progress
