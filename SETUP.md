# GCFB Dashboard - Setup Guide

This document provides step-by-step instructions for setting up the development environment.

## Project Structure Overview

The project is now initialized with the following structure:

```
GCFB/
├── frontend/              # React 18 + Vite application
│   ├── src/
│   │   ├── components/    # 5 component files (skeleton)
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── backend/               # Python FastAPI application
│   ├── routers/          # 4 API router files (skeleton)
│   ├── models/           # ML models directory
│   ├── data/             # Seed script + static data
│   ├── utils/            # Weather & equity utilities
│   ├── main.py           # FastAPI entry point
│   ├── db.py             # Database configuration
│   ├── schemas.py        # Pydantic models
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment template
│
├── spec.md               # Complete technical specification
├── milestones.md         # Project breakdown (10 milestones)
├── README.md             # Project overview
├── .gitignore            # Git ignore rules
└── SETUP.md              # This file
```

## Current Status

✅ **Completed:**
- All directories created
- All skeleton files created with structure comments
- Package configuration files ready
- Documentation files created

⏳ **Next Steps (follow milestones.md):**
1. Set up PostgreSQL database
2. Generate simulated data
3. Train ML model
4. Implement API endpoints
5. Implement frontend components

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cd backend
copy .env.example .env
# Edit .env with your settings:
# - DATABASE_URL
# - OPENWEATHER_API_KEY
# - etc.
```

### 3. Set Up Database

1. Install PostgreSQL 14+
2. Create database: `createdb gcfb`
3. Update DATABASE_URL in `.env`
4. Run seed script (once implemented):
   ```bash
   python data/seed.py
   ```

### 4. Run Development Servers

**Backend (Terminal 1):**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```
Access at: http://localhost:8000
API docs at: http://localhost:8000/docs

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```
Access at: http://localhost:3000

## Development Workflow

Follow the milestones in order:

1. **Milestone 1**: Database & Data Generation
   - Implement `backend/data/seed.py`
   - Create SQLAlchemy models in `backend/db.py`
   - Populate census and GeoJSON data

2. **Milestone 2**: ML Model Development
   - Build Random Forest model
   - Serialize to `backend/models/demand_model.pkl`

3. **Milestone 3**: Backend Core Infrastructure
   - Complete `backend/utils/weather.py`
   - Complete `backend/utils/equity.py`
   - Set up logging and error handling

4. **Milestones 4-5**: Backend API Implementation
   - Implement router endpoints
   - Complete `backend/schemas.py`
   - Test with API docs

5. **Milestones 6-8**: Frontend Implementation
   - Implement React components
   - Wire up API calls
   - Add state management

6. **Milestone 9**: Integration & Testing
   - End-to-end testing
   - Error handling verification
   - Demo flow validation

7. **Milestone 10**: Deployment
   - Logging and monitoring
   - Documentation updates
   - Deploy to hosting platform

## Useful Commands

### Backend
```bash
# Run backend
uvicorn main:app --reload

# Run seed script
python data/seed.py

# Format code
black .

# Type checking
mypy .
```

### Frontend
```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Endpoints (To Be Implemented)

- `GET /health` - Health check ✅ (basic implementation exists)
- `GET /forecast` - Get demand forecast by date
- `GET /forecast/{zip}` - Get detailed forecast for ZIP
- `POST /dispatch` - Generate optimized dispatch plan
- `GET /inventory/expiring` - Get expiring inventory items
- `GET /inventory/expiring/{item_id}/sites` - Get suggested sites
- `POST /dispatch/assign` - Assign item to dispatch plan
- `GET /sites` - Get all partner sites
- `GET /sites/{zip}` - Get sites by ZIP

## Components (To Be Implemented)

- `Map.jsx` - Leaflet heatmap with ZIP polygons
- `ZipSidePanel.jsx` - Detail panel for selected ZIP
- `DispatchPlanner.jsx` - Route optimization interface
- `ExpirationFeed.jsx` - Expiring inventory alerts
- `DateToggle.jsx` - Date selection (Today/Tomorrow/Week)

## External Dependencies

### Required Services
- PostgreSQL database
- OpenWeatherMap API key (free tier)

### Data Sources Needed
1. Ohio ZIP code GeoJSON (6-county area)
2. Census poverty data (ACS estimates)
3. Weather API integration

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure all dependencies installed

### Frontend won't build
- Delete node_modules and reinstall
- Clear npm cache: `npm cache clean --force`
- Check Node.js version (18+)

### Database connection issues
- Verify PostgreSQL service is running
- Check database exists: `psql -l`
- Test connection string

## Next Immediate Action

**Start with Milestone 1:**
1. Set up PostgreSQL locally
2. Implement database schema in `db.py`
3. Implement `seed.py` to generate realistic data
4. Verify data populated correctly

See `milestones.md` for detailed Definition of Done criteria.

## Resources

- Spec: `spec.md`
- Milestones: `milestones.md`
- FastAPI docs: https://fastapi.tiangolo.com/
- React docs: https://react.dev/
- Leaflet docs: https://leafletjs.com/
- OR-Tools docs: https://developers.google.com/optimization

---

**Ready to build!** Follow the milestones sequentially for best results.
