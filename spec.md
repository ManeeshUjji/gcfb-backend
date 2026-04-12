# Product Specification — GCFB Operational Intelligence Dashboard
### Proof of Concept | Greater Cleveland Food Bank Ideation Event

---

## 1. Overview

A web-based operational intelligence dashboard for the Greater Cleveland Food Bank (GCFB). It gives GCFB operations staff a single screen to:

1. See where food demand is expected to be high across their 6-county service area
2. Generate an optimized daily dispatch plan for trucks and volunteers
3. Get alerted when donated food is about to expire — with suggested partner sites to receive it

This is a **proof of concept built on simulated but realistic data.** It is not connected to GCFB's real systems. The goal is to demonstrate what is possible before a real integration is scoped with GCFB's operations team.

---

## 2. Problem Being Solved

GCFB serves 400,000+ people across 6 counties through 1,000+ partner sites. Demand fluctuates daily based on weather, economic conditions, end-of-month SNAP exhaustion, and local events. Supply is equally unpredictable — 30% of food is donated and arrives near expiration.

Currently, staff make dispatch and allocation decisions using spreadsheets, historical data, and experience. This makes it hard to react quickly to change and difficult to ensure equitable distribution to the highest-need communities.

---

## 3. Target User

**GCFB Operations Staff** — one user type for this demo.

Someone who shows up in the morning, needs to make decisions about where food and resources go today and this week, and currently does this manually. They are not a data scientist. The tool must be immediately understandable without training.

---

## 4. Data

### 4.1 Geography
- 6 counties: Cuyahoga, Lake, Geauga, Ashtabula, Trumbull, Portage
- Real ZIP codes within those counties
- Real GeoJSON boundaries for map rendering

### 4.2 Simulated Internal Data (seeded via script)
| Dataset | Description |
|---|---|
| Historical distribution records | 90 days of simulated headcount per ZIP per program type per day |
| Warehouse inventory | Item name, quantity, unit, expiration date |
| Partner site list | Name, ZIP, coordinates, program type, capacity, days of operation |
| Truck fleet | Number of trucks, capacity per truck (lbs) |
| Volunteer availability | Daily volunteer count (simulated with realistic variance) |

### 4.3 External Data (live)
| Source | Data | How |
|---|---|---|
| OpenWeatherMap API | Current + 7-day forecast for Cleveland area | REST API call, free tier |
| US Census ACS | Poverty rate by ZIP code | Static JSON file, pre-loaded once |

### 4.4 GeoJSON
- Ohio ZIP code boundaries for the 6-county area
- Source: publicly available US Census TIGER/Line shapefiles, converted to GeoJSON

---

## 5. Modules

---

### Module 1 — Demand Heatmap

#### What It Does
Renders a map of all 6 counties with ZIP codes colored by predicted demand level for a selected time window.

#### UI Elements
- Full-screen Leaflet.js map as the default landing view
- ZIP code polygons shaded green → yellow → red (low → high predicted demand)
- Date toggle at top: **Today | Tomorrow | This Week**
- Clicking a ZIP opens a right-side panel showing:
  - Predicted headcount range (e.g. "180–220 people expected")
  - % change vs same period last week
  - Top 3 contributing factors (e.g. "End of month", "Cold weather forecast", "High poverty index")
  - List of partner sites in that ZIP with program type and operating hours

#### How the Forecast Works
- Model: **Random Forest Classifier (scikit-learn)**
- Trained on: simulated 90-day historical dataset
- Input features:
  - ZIP code (encoded)
  - Day of week (0–6)
  - Day of month (1–31)
  - Program type (encoded)
  - Temperature forecast (°F)
  - Precipitation forecast (inches)
  - Census poverty rate for that ZIP
- Output: predicted headcount range per ZIP per day
- Model is **pre-trained and serialized** (`.pkl`) — it does not retrain live during the demo
- Feature importances from Random Forest are used to generate the "contributing factors" — this makes the forecast explainable in plain English

---

### Module 2 — Daily Dispatch Planner

#### What It Does
Takes today's available resources and generates an optimized dispatch plan — which truck goes where, carrying what, in what order — with an equity layer that prioritizes highest-need communities.

#### UI Elements
- Left panel: input fields
  - Number of trucks available (pre-filled from simulated fleet, editable)
  - Volunteer count today (pre-filled, editable)
  - Warehouse inventory summary (read from simulated inventory data)
- "Generate Today's Plan" button
- Right panel / map overlay: results
  - Truck route paths drawn on the Leaflet map (color-coded per truck)
  - Text plan below map: "Truck 1 → Site A (120 lbs) → Site B (80 lbs) → Site C (200 lbs)"
  - Print / export button (simple print CSS)

#### How the Optimization Works
- Library: **Google OR-Tools** (vehicle routing problem solver)
- Inputs to the solver:
  - Number of trucks and capacity per truck
  - Partner site locations (lat/lng)
  - Forecasted demand per site (from Module 1 model output)
  - Equity weight per ZIP (derived from census poverty index — higher poverty = higher priority weight)
- Equity layer: sites in higher-need ZIPs receive a priority multiplier so they are served earlier in the route before lower-need areas
- Output: ordered list of stops per truck with quantities
- This is **fully deterministic** — no AI, no black box. OR-Tools is a constraint solver. The output is auditable and explainable.

---

### Module 3 — Expiration Alert Feed

#### What It Does
Surfaces warehouse inventory items expiring within 72 hours and suggests partner sites to receive them, with one-click assignment into the dispatch plan.

#### UI Elements
- Persistent sidebar or dedicated tab
- List of expiring items:
  - Item name, quantity, expiration date
  - Days remaining (color coded: red < 24hrs, orange < 72hrs)
  - "Find Sites" button per item
- On "Find Sites" click:
  - Returns top 3 suggested partner sites
  - Ranked by: proximity + forecasted demand + remaining capacity
- "Assign" button next to each suggested site
  - Clicking assign adds that delivery to the dispatch plan in Module 2
  - Module 2 updates automatically

#### How the Matching Works
- **No AI** — pure rules-based logic
- Algorithm:
  1. Filter partner sites to those operating today or tomorrow
  2. Score each site: `score = (1/distance_km) * demand_forecast * (1 - current_fill_rate)`
  3. Return top 3 by score
- Fast, transparent, reliable

---

## 6. Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React 18 + Vite | Fast dev build |
| Styling | Tailwind CSS | Utility-first, consistent spacing |
| Map | Leaflet.js + react-leaflet | ZIP polygon rendering + route overlay |
| Charts | Recharts | Demand trend sparklines in side panel |
| Backend | Python 3.11 + FastAPI | Lightweight REST API |
| Forecasting | scikit-learn (Random Forest) | Pre-trained, serialized as .pkl |
| Routing Optimization | Google OR-Tools (ortools Python package) | Vehicle routing problem solver |
| Database | PostgreSQL | Stores all simulated data |
| ORM | SQLAlchemy | DB access layer |
| Simulated Data | Python seed script | Run once to populate DB |
| Weather | OpenWeatherMap API | Free tier, current + 7-day forecast |
| Census Data | Static JSON | ACS poverty estimates by ZIP, pre-loaded |
| GeoJSON | Static file | Ohio ZIP boundaries, 6-county area |
| Hosting | Render or Railway | Free tier, sufficient for demo |

---

## 7. Project File Structure

```
/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map.jsx                  # Leaflet heatmap + route overlay
│   │   │   ├── ZipSidePanel.jsx         # Detail panel on ZIP click
│   │   │   ├── DispatchPlanner.jsx      # Input panel + plan output
│   │   │   ├── ExpirationFeed.jsx       # Alert sidebar
│   │   │   └── DateToggle.jsx           # Today / Tomorrow / This Week
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── backend/
│   ├── main.py                          # FastAPI app entry point
│   ├── routers/
│   │   ├── forecast.py                  # GET /forecast?zip=&date= → predicted demand
│   │   ├── dispatch.py                  # POST /dispatch → optimized truck plan
│   │   ├── inventory.py                 # GET /inventory/expiring → alert feed
│   │   └── sites.py                     # GET /sites → partner site list + details
│   ├── models/
│   │   └── demand_model.pkl             # Pre-trained Random Forest model
│   ├── data/
│   │   ├── seed.py                      # Script to generate + insert simulated data
│   │   ├── census_poverty.json          # Static ZIP-level poverty index
│   │   └── ohio_zips.geojson            # GeoJSON boundaries for 6-county area
│   ├── utils/
│   │   ├── weather.py                   # OpenWeatherMap API wrapper
│   │   └── equity.py                    # Poverty index loader + weighting logic
│   ├── db.py                            # SQLAlchemy setup + session
│   ├── schemas.py                       # Pydantic models for request/response
│   └── requirements.txt
│
└── README.md
```

---

## 8. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/forecast` | Returns predicted demand per ZIP. Params: `date` (today/tomorrow/week) |
| GET | `/forecast/{zip}` | Returns detailed forecast + contributing factors for a single ZIP |
| POST | `/dispatch` | Accepts truck count + volunteer count, returns optimized route plan |
| GET | `/inventory/expiring` | Returns items expiring within 72 hours |
| GET | `/inventory/expiring/{item_id}/sites` | Returns top 3 suggested partner sites for an expiring item |
| POST | `/dispatch/assign` | Adds an expiration assignment into the current dispatch plan |
| GET | `/sites` | Returns full partner site list with coordinates and program types |
| GET | `/sites/{zip}` | Returns partner sites within a specific ZIP |

---

## 9. Simulated Data Spec

The seed script (`data/seed.py`) must generate realistic data for the demo. Here is what it needs to produce:

### Partner Sites
- 40–60 simulated partner sites spread across the 6 counties
- Each has: name, address, ZIP, lat/lng, program type (pantry / senior / kids café / mobile / shelter), capacity (people/day), days of operation (e.g. Mon/Wed/Fri)

### Historical Distribution
- 90 days of records
- Each record: site_id, date, headcount, program_type
- Must encode realistic patterns:
  - Higher headcount on 1st and 15th of each month (SNAP exhaustion)
  - Higher headcount in winter months
  - Lower headcount on weekends
  - Some ZIPs consistently higher than others (poverty-correlated)

### Warehouse Inventory
- 15–25 simulated items
- Each has: name, category (produce/dairy/dry goods/protein), quantity, unit, expiration_date
- At least 3–5 items should be within 72 hours of expiration for the demo

### Truck Fleet
- 5 trucks
- Capacity: 500–800 lbs per truck (vary per truck)

### Volunteer Count
- Simulated as a daily number between 80–150 with random variance

---

## 10. Demo Flow (Under 3 Minutes)

1. App opens on the heatmap — Cleveland map renders, ZIP codes light up red/yellow/green
2. Presenter points to red ZIPs — "these are the high-need areas predicted for today"
3. Click a red ZIP → side panel opens showing predicted headcount, contributing factors, partner sites
4. Toggle to "Tomorrow" → map updates with different heat distribution
5. Navigate to Dispatch Planner tab → enter today's trucks and volunteers → click "Generate Plan"
6. Truck routes appear on map, text plan populates below
7. Point to equity layer — "notice the highest poverty ZIPs are served first"
8. Navigate to Expiration Alerts → 3 items show, click "Find Sites" on one → top 3 partners appear
9. Click "Assign" → dispatch plan updates automatically
10. Done

---

## 11. What This Is Not

- Not connected to GCFB's real data, inventory systems, or partner network
- Not a final product — it is a proof of concept to demonstrate feasibility
- Not autonomous — every recommendation requires a human to confirm before action
- Not a black box — every output (forecast, route, alert match) can be explained in plain English to a non-technical staff member

---

## 12. Open Questions (For Real Implementation)

These are questions that would need to be answered before building the production version:

- How does GCFB currently track warehouse inventory? (WMS, spreadsheet, other?)
- How do partner sites communicate their current capacity and needs back to GCFB?
- How is the truck fleet currently managed and dispatched?
- What systems does the Help Center use during phone calls?
- Is there existing data infrastructure (data warehouse, BI tool) to integrate with?
- What are the IT and budget constraints for hosting and maintenance?

---

## 13. Build Order (Recommended for Cursor)

1. Set up PostgreSQL schema + seed script — get realistic data in the DB first
2. Build and train the Random Forest model on the seeded data, serialize to `.pkl`
3. Build FastAPI backend — all endpoints, model inference, OR-Tools integration
4. Build React frontend shell — routing, layout, Tailwind config
5. Build Map component with GeoJSON ZIP polygons + color shading from forecast API
6. Build ZIP side panel
7. Build date toggle wired to forecast API
8. Build Dispatch Planner — inputs + OR-Tools call + route rendering on map
9. Build Expiration Alert Feed + site matching + assign flow
10. Wire everything together, test full demo flow end to end
11. Deploy to Render or Railway
