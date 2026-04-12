# Project Milestones — GCFB Operational Intelligence Dashboard

This document breaks down the GCFB Operational Intelligence Dashboard proof-of-concept into atomic, independent tasks. Each milestone has a clear Definition of Done to ensure quality and completeness.

---

## Milestone 1: Database Schema & Simulated Data Generation

**Owner:** Backend Developer  
**Priority:** Critical (Blocking)  
**Estimated Effort:** 2-3 days

### Scope
Set up PostgreSQL database schema and generate realistic simulated data for all modules.

### Tasks
- Design and implement database schema with tables for:
  - Partner sites (name, address, ZIP, lat/lng, program type, capacity, operating days)
  - Historical distribution records (90 days, site_id, date, headcount, program_type)
  - Warehouse inventory (item name, category, quantity, unit, expiration_date)
  - Truck fleet (truck_id, capacity_lbs)
  - Volunteer availability (date, volunteer_count)
- Build seed script (`backend/data/seed.py`) to generate realistic data with encoded patterns:
  - SNAP exhaustion spikes (1st and 15th of month)
  - Seasonal variations (higher winter demand)
  - Weekend patterns (lower weekend demand)
  - Poverty-correlated ZIP variance
- Ensure 3-5 inventory items expire within 72 hours for demo purposes
- Create SQLAlchemy ORM models matching schema

### Definition of Done
- [x] PostgreSQL database deployed locally with all tables created (SQLite used for development, PostgreSQL ready for production)
- [x] Seed script runs without errors and populates all tables
- [x] Database contains 40-60 partner sites across 6 counties
- [x] 90 days of historical distribution data with realistic patterns verified
- [x] 15-25 warehouse inventory items with 3-5 expiring within 72 hours
- [x] 5 trucks and 90 days of volunteer data generated
- [x] SQLAlchemy models tested with basic CRUD operations
- [x] Database connection string documented in README

---

## Milestone 2: Machine Learning Model Development & Serialization

**Owner:** Data Scientist / ML Engineer  
**Priority:** Critical (Blocking for Module 1)  
**Estimated Effort:** 3-4 days

### Scope
Build, train, and serialize a Random Forest model for demand forecasting using the seeded historical data.

### Tasks
- Load historical distribution data, weather patterns (simulated), and census poverty data
- Engineer features:
  - ZIP code (one-hot or ordinal encoding)
  - Day of week (0-6)
  - Day of month (1-31)
  - Program type (encoded)
  - Temperature and precipitation (simulated historical + forecast data)
  - Census poverty rate by ZIP
- Train Random Forest Classifier on 90-day dataset
- Evaluate model performance (accuracy, precision, recall)
- Extract and document feature importances for explainability
- Serialize model to `backend/models/demand_model.pkl`
- Create model inference utility function for API integration

### Definition of Done
- [x] Model trained on full 90-day simulated dataset
- [x] Model achieves reasonable performance metrics (documented in notebook or script)
- [x] Feature importances extracted and ranked
- [x] Serialized `.pkl` file saved in `backend/models/`
- [x] Inference function created and tested with sample inputs
- [x] Model outputs headcount predictions for given ZIP, date, and features
- [x] Documentation includes model architecture, feature list, and usage examples

---

## Milestone 3: Backend API Core Infrastructure

**Owner:** Backend Developer  
**Priority:** Critical (Blocking for all modules)  
**Estimated Effort:** 2-3 days

### Scope
Set up FastAPI application with core infrastructure, external API integrations, and foundational utilities.

### Tasks
- Initialize FastAPI app (`backend/main.py`) with CORS middleware
- Set up SQLAlchemy session management (`backend/db.py`)
- Create Pydantic schemas for all request/response models (`backend/schemas.py`)
- Build OpenWeatherMap API wrapper (`backend/utils/weather.py`) with:
  - Current weather fetching
  - 7-day forecast fetching
  - Error handling and retry logic for API failures
  - Caching mechanism to avoid rate limits
- Build equity utility module (`backend/utils/equity.py`) to:
  - Load census poverty data from JSON
  - Calculate equity weights by ZIP code
- Implement centralized error handling middleware
- Set up structured logging (with timestamps, endpoint, params, errors)
- Create health check endpoint (`GET /health`)

### Definition of Done
- [x] FastAPI app runs locally on default port
- [x] Database connection established and tested
- [x] All Pydantic schemas defined for API contracts
- [x] OpenWeatherMap API integration working with fallback for failures
- [x] Census poverty data loaded and accessible via utility function
- [x] Centralized error handling returns consistent error responses
- [x] Logging outputs to console/file with structured format
- [x] Health check endpoint returns 200 OK with system status

---

## Milestone 4: Backend API Endpoints - Forecast & Sites

**Owner:** Backend Developer  
**Priority:** High (Blocking for Module 1)  
**Estimated Effort:** 3-4 days

### Scope
Implement forecast and site-related API endpoints using the trained ML model.

### Tasks
- Build `/forecast` endpoint (GET):
  - Accept `date` parameter (today/tomorrow/week)
  - Load weather forecast data for date range
  - Run model inference for all ZIPs
  - Return predicted demand per ZIP with color-coding thresholds
- Build `/forecast/{zip}` endpoint (GET):
  - Return detailed forecast for a single ZIP
  - Include predicted headcount range
  - Calculate % change vs same period last week
  - Extract top 3 contributing factors using feature importances
  - List partner sites in that ZIP
- Build `/sites` endpoint (GET):
  - Return full partner site list with coordinates and program types
- Build `/sites/{zip}` endpoint (GET):
  - Return partner sites filtered by ZIP code
- Implement comprehensive error handling for all endpoints
- Add request validation and logging

### Definition of Done
- [x] All four endpoints implemented and testable via Swagger/ReDoc
- [x] `/forecast` returns predictions for all ZIPs in 6-county area
- [x] `/forecast/{zip}` returns detailed forecast with contributing factors
- [x] `/sites` and `/sites/{zip}` return correct partner site data
- [x] Error responses include clear messages and appropriate HTTP status codes
- [x] All requests/responses logged with timestamps and parameters
- [x] Endpoints tested with Postman or equivalent (test collection documented)
- [x] Response times under 2 seconds for forecast endpoints

---

## Milestone 5: Backend API Endpoints - Dispatch & Inventory

**Owner:** Backend Developer  
**Priority:** High (Blocking for Modules 2 & 3)  
**Estimated Effort:** 4-5 days

### Scope
Implement dispatch optimization and inventory alert endpoints using OR-Tools.

### Tasks
- Build `POST /dispatch` endpoint:
  - Accept truck count, volunteer count, and optional constraints
  - Fetch forecasted demand per site from Module 1
  - Apply equity weights (poverty index) to prioritize high-need ZIPs
  - Run OR-Tools vehicle routing solver
  - Return optimized route plan with ordered stops per truck
  - Include total distance, estimated time, and quantities per stop
- Build `GET /inventory/expiring` endpoint:
  - Query warehouse inventory for items expiring within 72 hours
  - Return list with item details and days remaining
  - Color-code urgency (red < 24hrs, orange < 72hrs)
- Build `GET /inventory/expiring/{item_id}/sites` endpoint:
  - Filter partner sites operating today or tomorrow
  - Calculate score: `(1/distance_km) * demand_forecast * (1 - current_fill_rate)`
  - Return top 3 suggested partner sites
- Build `POST /dispatch/assign` endpoint:
  - Accept item_id and site_id
  - Add assignment to dispatch plan state
  - Return updated dispatch plan
- Implement state management for active dispatch plans (in-memory or Redis)

### Definition of Done
- [x] `POST /dispatch` endpoint generates optimized truck routes using OR-Tools
- [x] Equity layer verified: highest poverty ZIPs served first in routes
- [x] `GET /inventory/expiring` returns items expiring within 72 hours
- [x] `GET /inventory/expiring/{item_id}/sites` returns top 3 partner matches
- [x] `POST /dispatch/assign` successfully updates dispatch plan state
- [x] All endpoints handle edge cases (no expiring items, insufficient trucks, etc.)
- [x] Error handling and logging in place for all endpoints
- [x] Endpoints tested and response times documented
- [x] OR-Tools integration verified with sample scenarios

---

## Milestone 6: Frontend Core Infrastructure & Map Module (Module 1)

**Owner:** Frontend Developer  
**Priority:** High  
**Estimated Effort:** 4-5 days

### Scope
Build React application shell and implement the demand heatmap module with interactive ZIP selection.

### Tasks
- Initialize React 18 + Vite project with Tailwind CSS
- Set up routing structure for three main views (Heatmap, Dispatch, Alerts)
- Implement global state management (Context API or Redux) for:
  - Selected date (today/tomorrow/week)
  - Active dispatch plan
  - User inputs (truck count, volunteer count)
- Build `Map.jsx` component:
  - Integrate Leaflet.js and react-leaflet
  - Load Ohio GeoJSON for 6-county ZIP boundaries
  - Fetch forecast data from `/forecast` API
  - Color ZIP polygons based on demand (green → yellow → red)
  - Handle map interactions (zoom, pan, click)
- Build `DateToggle.jsx` component:
  - Toggle between Today / Tomorrow / This Week
  - Update global state and trigger map refresh
- Build `ZipSidePanel.jsx` component:
  - Display on ZIP click
  - Show predicted headcount range
  - Show % change vs last week
  - Display top 3 contributing factors
  - List partner sites in ZIP with program types and hours
- Implement loading states and error notifications for API calls
- Add responsive design for tablet and desktop

### Definition of Done
- [x] React app runs locally with Vite dev server
- [x] Tailwind CSS configured and working
- [x] Map renders with 6-county Ohio ZIP boundaries
- [x] ZIP polygons color-coded correctly based on forecast API data
- [x] Date toggle updates map in real-time
- [x] Clicking ZIP opens side panel with correct detailed information
- [x] Loading indicators display during API calls
- [x] Error notifications display when API calls fail
- [x] UI is responsive and usable on desktop and tablet
- [x] All components properly manage state transitions

---

## Milestone 7: Frontend Dispatch Planner Module (Module 2)

**Owner:** Frontend Developer  
**Priority:** High  
**Estimated Effort:** 3-4 days

### Scope
Build the dispatch planner interface with input controls, route visualization, and export functionality.

### Tasks
- Build `DispatchPlanner.jsx` component with:
  - Left panel: input fields for truck count and volunteer count
  - Warehouse inventory summary display (read-only)
  - "Generate Today's Plan" button
  - Right panel: results display area
- Implement dispatch plan generation flow:
  - Validate inputs (truck count > 0, volunteer count >= 0)
  - Call `POST /dispatch` API with parameters
  - Handle loading state during optimization
  - Display success/error feedback
- Visualize results on map:
  - Draw truck route paths on Leaflet map (color-coded per truck)
  - Add markers for each stop with tooltips
  - Display route order and quantities
- Build text plan output:
  - Format as "Truck 1 → Site A (120 lbs) → Site B (80 lbs)"
  - Include total distance and estimated time per truck
- Add print/export button with print-friendly CSS
- Ensure state synchronization when assignments added from Module 3

### Definition of Done
- [x] Dispatch planner UI matches design specification
- [x] Input fields pre-filled with simulated data and editable
- [x] "Generate Today's Plan" button triggers API call
- [x] Loading indicator displays during optimization
- [x] Truck routes rendered on map with color-coded paths
- [x] Text plan displays correctly formatted route details
- [x] Print/export functionality works and produces readable output
- [x] Error handling displays clear messages for failures
- [x] Module updates automatically when expiration assignments added
- [x] State management ensures consistency across modules

---

## Milestone 8: Frontend Expiration Alert Module (Module 3)

**Owner:** Frontend Developer  
**Priority:** Medium  
**Estimated Effort:** 3-4 days

### Scope
Build the expiration alert feed with site matching and one-click assignment to dispatch plan.

### Tasks
- Build `ExpirationFeed.jsx` component:
  - Persistent sidebar or dedicated tab view
  - Fetch data from `GET /inventory/expiring` API
  - Display list of expiring items with color-coded urgency
  - Show item name, quantity, expiration date, days remaining
- Implement "Find Sites" flow:
  - Button per expiring item
  - Call `GET /inventory/expiring/{item_id}/sites` API
  - Display top 3 suggested partner sites with:
    - Site name and location
    - Forecasted demand
    - Proximity distance
    - Match score explanation
- Implement "Assign" flow:
  - Button next to each suggested site
  - Call `POST /dispatch/assign` API
  - Show success confirmation
  - Trigger update in Dispatch Planner module
  - Update local state to reflect assignment
- Add loading states for site matching
- Implement error handling for assignment failures

### Definition of Done
- [x] Expiration alert feed displays correctly in UI
- [x] Items color-coded by urgency (red < 24hrs, orange < 72hrs)
- [x] "Find Sites" button triggers API call and displays top 3 matches
- [x] Match results show site details and ranking explanation
- [x] "Assign" button adds delivery to dispatch plan
- [x] Dispatch Planner module updates automatically on assignment
- [x] Loading indicators display during site matching
- [x] Error notifications display for API failures
- [x] UI provides clear feedback on successful assignments
- [x] State management ensures consistency with Dispatch module

---

## Milestone 9: Integration, Testing & Demo Flow Validation

**Owner:** Full Stack Developer / QA  
**Priority:** Critical  
**Estimated Effort:** 3-4 days

### Scope
Integrate all modules, implement comprehensive error handling, validate complete demo flow, and ensure production readiness.

### Tasks
- End-to-end integration testing:
  - Test complete demo flow (Section 10 of spec)
  - Verify all module interactions work seamlessly
  - Test state synchronization between modules
- Implement frontend error boundary component
- Add toast notifications for user feedback across all actions
- Verify fallback behavior when external APIs fail (OpenWeatherMap)
- Performance testing:
  - Measure API response times under load
  - Optimize slow queries or computations
  - Test with larger datasets (if applicable)
- Cross-browser testing (Chrome, Firefox, Edge)
- Mobile responsiveness verification
- Accessibility audit (WCAG 2.1 Level AA basics)
- Create test scenarios document covering:
  - Happy path flows
  - Error cases
  - Edge cases (no trucks, no expiring items, API failures)

### Definition of Done
- [x] Complete demo flow (10 steps in spec) executes without errors
- [x] All module interactions tested and working correctly
- [x] Error boundaries catch and display frontend errors gracefully
- [x] Toast notifications provide clear feedback for all user actions
- [x] External API failures handled with appropriate fallbacks
- [x] API response times documented and within acceptable limits
- [x] Application works correctly in Chrome, Firefox, and Edge
- [x] UI is usable on tablet devices (responsive design verified)
- [x] Basic accessibility requirements met (keyboard navigation, ARIA labels)
- [x] Test scenarios document created and all scenarios passing
- [x] Known issues documented with severity ratings

---

## Milestone 10: Logging, Monitoring, Documentation & Deployment

**Owner:** DevOps / Technical Writer  
**Priority:** High  
**Estimated Effort:** 3-4 days

### Scope
Implement production-grade logging and monitoring, create comprehensive documentation, and deploy to hosting platform.

### Tasks
- Backend logging enhancements:
  - Configure structured logging with log levels (DEBUG, INFO, WARNING, ERROR)
  - Log all API requests with timestamps, endpoints, parameters
  - Log all errors with stack traces
  - Set up log rotation and retention policy
- Monitoring setup:
  - Integrate health check endpoint into monitoring
  - Set up basic performance metrics tracking
  - Configure alerting for critical failures (if using free tier tools)
  - Document monitoring approach for production expansion
- Documentation:
  - Update README.md with:
    - Project overview and goals
    - Setup instructions (database, backend, frontend)
    - Environment variables and configuration
    - Running the application locally
    - Demo flow walkthrough
  - Create API documentation (Swagger/ReDoc auto-generated + custom descriptions)
  - Document architecture decisions and trade-offs
  - Create maintenance guide covering:
    - Model retraining process
    - Data refresh procedures
    - Common troubleshooting steps
  - Ensure all documentation is SEO optimized (per user rules)
- Deployment:
  - Deploy PostgreSQL database (Railway, Supabase, or Render)
  - Deploy FastAPI backend to Render/Railway
  - Deploy React frontend to Netlify/Vercel/Render
  - Configure environment variables for production
  - Test deployed application end-to-end
  - Set up CI/CD pipeline (optional for POC)

### Definition of Done
- [ ] Backend logs all requests and errors with structured format
- [ ] Logging outputs captured and accessible (file or cloud logging service)
- [ ] Health check endpoint monitored and reporting correct status
- [ ] Basic performance metrics tracked (response times, error rates)
- [ ] Alerting configured for critical failures (if using free tier tools)
- [ ] README.md complete with setup and usage instructions
- [ ] API documentation accessible and comprehensive
- [ ] Maintenance guide created with model retraining procedures
- [ ] All documentation SEO optimized and clearly written
- [ ] Application deployed and accessible via public URL
- [ ] Production environment variables configured correctly
- [ ] End-to-end test passed on deployed application
- [ ] Deployment process documented for future updates
- [ ] Demo ready to present to stakeholders

---

## Summary

| Milestone | Priority | Estimated Effort | Dependencies |
|-----------|----------|------------------|--------------|
| 1. Database & Data Generation | Critical | 2-3 days | None |
| 2. ML Model Development | Critical | 3-4 days | Milestone 1 |
| 3. Backend Core Infrastructure | Critical | 2-3 days | Milestone 1 |
| 4. Backend Forecast & Sites APIs | High | 3-4 days | Milestones 2, 3 |
| 5. Backend Dispatch & Inventory APIs | High | 4-5 days | Milestones 2, 3 |
| 6. Frontend Core & Map Module | High | 4-5 days | Milestone 4 |
| 7. Frontend Dispatch Planner | High | 3-4 days | Milestones 5, 6 |
| 8. Frontend Expiration Alert | Medium | 3-4 days | Milestones 5, 6 |
| 9. Integration & Testing | Critical | 3-4 days | Milestones 1-8 |
| 10. Logging, Monitoring & Deployment | High | 3-4 days | Milestone 9 |

**Total Estimated Effort:** 30-40 days (individual contributor time)

---

## Notes

- Milestones 1-3 are foundational and must be completed before other work can begin
- Milestones 4-5 (Backend APIs) and 6-8 (Frontend Modules) can be developed in parallel by separate team members
- Milestone 9 (Integration & Testing) is critical and should not be skipped
- Milestone 10 (Deployment) can begin once Milestone 9 passes all tests
- Each milestone includes built-in quality checks through the Definition of Done criteria
- This breakdown assumes a small team (2-3 developers) working in parallel where possible
