# Milestone 1 Implementation Plan: Database Schema & Simulated Data Generation

**Strictly Technical Plan for AI Implementation**

---

## Files to Create/Modify

### 1. `backend/db.py` - Complete database setup and ORM models
### 2. `backend/data/seed.py` - Complete data generation script
### 3. `backend/data/zip_coordinates.py` - Helper with ZIP code data for 6 counties
### 4. `backend/.env` - Environment configuration (copy from .env.example)

---

## Database Schema Specification

### Table 1: `partner_sites`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | |
| name | VARCHAR(200) | NOT NULL | |
| address | VARCHAR(300) | NOT NULL | |
| zip_code | VARCHAR(10) | NOT NULL | Must be from 6-county area |
| latitude | FLOAT | NOT NULL | Decimal degrees |
| longitude | FLOAT | NOT NULL | Decimal degrees |
| program_type | VARCHAR(50) | NOT NULL | ENUM: pantry, senior, kids_cafe, mobile, shelter |
| capacity_per_day | INTEGER | NOT NULL | People per day, range: 50-500 |
| operating_days | VARCHAR(50) | NOT NULL | Comma-separated, e.g. "Mon,Wed,Fri" or "Mon-Fri" |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:** 
- `idx_partner_sites_zip` on `zip_code`
- `idx_partner_sites_program` on `program_type`

### Table 2: `historical_distribution`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | |
| site_id | INTEGER | FOREIGN KEY -> partner_sites.id, NOT NULL | |
| date | DATE | NOT NULL | |
| headcount | INTEGER | NOT NULL | Range: 20-800 |
| program_type | VARCHAR(50) | NOT NULL | Must match site's program_type |
| temperature_f | FLOAT | NULL | Simulated weather for that day |
| precipitation_inches | FLOAT | NULL | Simulated weather for that day |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- `idx_historical_date` on `date`
- `idx_historical_site` on `site_id`
- Composite: `idx_historical_site_date` on `(site_id, date)`

**Constraints:**
- UNIQUE constraint on `(site_id, date)` to prevent duplicates

### Table 3: `warehouse_inventory`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | |
| item_name | VARCHAR(200) | NOT NULL | |
| category | VARCHAR(50) | NOT NULL | ENUM: produce, dairy, dry_goods, protein, frozen |
| quantity | FLOAT | NOT NULL | Amount available |
| unit | VARCHAR(20) | NOT NULL | lbs, kg, cases, items |
| expiration_date | DATE | NOT NULL | |
| received_date | DATE | NOT NULL | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- `idx_inventory_expiration` on `expiration_date`
- `idx_inventory_category` on `category`

### Table 4: `truck_fleet`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | |
| truck_number | VARCHAR(20) | NOT NULL, UNIQUE | e.g., "TRUCK-001" |
| capacity_lbs | INTEGER | NOT NULL | Range: 500-800 |
| status | VARCHAR(20) | NOT NULL | ENUM: active, maintenance, inactive |
| created_at | TIMESTAMP | DEFAULT NOW() | |

### Table 5: `volunteer_availability`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | |
| date | DATE | NOT NULL, UNIQUE | |
| volunteer_count | INTEGER | NOT NULL | Range: 80-150 |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Indexes:**
- `idx_volunteer_date` on `date`

---

## Implementation Details

### File: `backend/data/zip_coordinates.py`

**Purpose:** Provide real ZIP codes with coordinates for 6-county area.

```python
# Data structure
COUNTIES = {
    "Cuyahoga": [...],
    "Lake": [...],
    "Geauga": [...],
    "Ashtabula": [...],
    "Trumbull": [...],
    "Portage": [...]
}

# Each entry: {"zip": "44101", "lat": 41.5034, "lon": -81.6934, "poverty_rate": 0.25}
```

**Function:**
- `get_all_zips() -> List[Dict]` - Returns all ZIP codes with coordinates
- `get_random_zip(county: Optional[str] = None) -> Dict` - Returns random ZIP from specified county or all
- `get_high_poverty_zips(threshold: float = 0.20) -> List[Dict]` - Returns ZIPs above poverty threshold

**Data Required:** 15-20 real ZIP codes per county with actual lat/lon coordinates.

---

### File: `backend/db.py`

#### SQLAlchemy Models

**Import Structure:**
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv
```

**Classes to Define:**

1. **`Base = declarative_base()`**

2. **`PartnerSite(Base)`**
   - `__tablename__ = 'partner_sites'`
   - All columns as per schema
   - `__repr__` method for debugging

3. **`HistoricalDistribution(Base)`**
   - `__tablename__ = 'historical_distribution'`
   - All columns as per schema
   - Relationship: `site = relationship("PartnerSite", back_populates="distributions")`
   - `__table_args__ = (UniqueConstraint('site_id', 'date', name='unique_site_date'),)`

4. **`WarehouseInventory(Base)`**
   - `__tablename__ = 'warehouse_inventory'`
   - All columns as per schema

5. **`TruckFleet(Base)`**
   - `__tablename__ = 'truck_fleet'`
   - All columns as per schema

6. **`VolunteerAvailability(Base)`**
   - `__tablename__ = 'volunteer_availability'`
   - All columns as per schema

**Functions:**

1. **`get_engine(database_url: Optional[str] = None)`**
   - Load DATABASE_URL from environment or parameter
   - Create and return SQLAlchemy engine
   - Add `echo=True` for development

2. **`init_db(engine)`**
   - Drop all existing tables: `Base.metadata.drop_all(bind=engine)`
   - Create all tables: `Base.metadata.create_all(bind=engine)`

3. **`get_session(engine)`**
   - Create SessionLocal: `sessionmaker(autocommit=False, autoflush=False, bind=engine)`
   - Return session instance

---

### File: `backend/data/seed.py`

#### Import Requirements:
```python
import random
import sys
from datetime import datetime, timedelta, date
from typing import List, Tuple
sys.path.append('..')
from db import (
    get_engine, init_db, get_session,
    PartnerSite, HistoricalDistribution, WarehouseInventory,
    TruckFleet, VolunteerAvailability
)
from data.zip_coordinates import get_all_zips, get_random_zip, get_high_poverty_zips
```

#### Constants:
```python
# Date ranges
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=90)

# Generation ranges
NUM_SITES_RANGE = (40, 60)
NUM_INVENTORY_RANGE = (15, 25)
NUM_TRUCKS = 5
EXPIRING_SOON_COUNT = 5  # Items expiring within 72 hours

# Program types
PROGRAM_TYPES = ['pantry', 'senior', 'kids_cafe', 'mobile', 'shelter']

# Item categories
ITEM_CATEGORIES = {
    'produce': ['Apples', 'Bananas', 'Carrots', 'Lettuce', 'Tomatoes', 'Potatoes', 'Onions'],
    'dairy': ['Milk', 'Cheese', 'Yogurt', 'Butter', 'Eggs'],
    'dry_goods': ['Rice', 'Pasta', 'Canned Beans', 'Canned Corn', 'Cereal', 'Oatmeal', 'Flour'],
    'protein': ['Chicken', 'Ground Beef', 'Pork', 'Canned Tuna', 'Peanut Butter'],
    'frozen': ['Frozen Vegetables', 'Frozen Fruit', 'Frozen Pizza', 'Ice Cream']
}

# Operating day patterns
OPERATING_PATTERNS = [
    'Mon,Wed,Fri',
    'Tue,Thu',
    'Mon,Tue,Wed,Thu,Fri',
    'Mon,Wed',
    'Tue,Thu,Sat',
    'Mon-Fri',
    'Mon,Tue,Thu,Fri'
]
```

#### Function 1: `generate_partner_sites(session, num_sites: int) -> List[PartnerSite]`

**Logic:**
1. Get all available ZIP codes from `get_all_zips()`
2. For each site (range 1 to num_sites):
   - Select random ZIP from list
   - Generate name: `f"{program_type.title()} at {zip_code}"`
   - Generate address: `f"{random.randint(100, 9999)} Main St, ZIP {zip_code}"`
   - Select random program_type from PROGRAM_TYPES
   - Use ZIP's lat/lon coordinates
   - Generate capacity: `random.randint(50, 500)`
   - Select random operating_days from OPERATING_PATTERNS
3. Add all to session, commit in batch
4. Return list of created sites

**Pitfall:** Ensure ZIP codes are distributed across all 6 counties, not clustered.

#### Function 2: `calculate_headcount_multiplier(date: date, zip_poverty_rate: float) -> float`

**Logic:**
1. **Base multiplier = 1.0**
2. **SNAP exhaustion pattern:**
   - If day of month is 1 or 2: multiply by 1.4
   - If day of month is 15 or 16: multiply by 1.3
   - If day of month is 28-31: multiply by 1.2
3. **Seasonal pattern:**
   - If month in [12, 1, 2] (winter): multiply by 1.3
   - If month in [11, 3] (late fall/early spring): multiply by 1.15
   - If month in [6, 7, 8] (summer): multiply by 0.9
4. **Weekend pattern:**
   - If weekday in [5, 6] (Sat, Sun): multiply by 0.6
5. **Poverty correlation:**
   - If poverty_rate > 0.25: multiply by 1.3
   - If poverty_rate > 0.20: multiply by 1.15
6. Return final multiplier

#### Function 3: `calculate_base_headcount(program_type: str, capacity: int) -> int`

**Logic:**
```python
# Base utilization rates by program type
utilization = {
    'pantry': 0.75,
    'senior': 0.65,
    'kids_cafe': 0.80,
    'mobile': 0.70,
    'shelter': 0.85
}
base = int(capacity * utilization[program_type])
# Add random variance: ±15%
variance = random.uniform(0.85, 1.15)
return int(base * variance)
```

#### Function 4: `generate_weather_data(date: date) -> Tuple[float, float]`

**Logic:**
```python
# Cleveland winter/summer patterns
month = date.month
if month in [12, 1, 2]:  # Winter
    temp = random.uniform(20, 38)
    precip = random.uniform(0.05, 0.3)
elif month in [6, 7, 8]:  # Summer
    temp = random.uniform(68, 85)
    precip = random.uniform(0, 0.2)
elif month in [3, 4, 5]:  # Spring
    temp = random.uniform(45, 65)
    precip = random.uniform(0.1, 0.4)
else:  # Fall
    temp = random.uniform(40, 60)
    precip = random.uniform(0.05, 0.25)
return (temp, precip)
```

#### Function 5: `generate_historical_distribution(session, sites: List[PartnerSite], start_date: date, end_date: date)`

**Logic:**
1. Get ZIP poverty data mapping: `zip_poverty = {z['zip']: z['poverty_rate'] for z in get_all_zips()}`
2. For each site in sites:
   - Get site's poverty rate from zip_poverty
   - For each date from start_date to end_date:
     - Generate weather data: `temp, precip = generate_weather_data(date)`
     - Calculate base headcount: `base = calculate_base_headcount(site.program_type, site.capacity_per_day)`
     - Calculate multiplier: `mult = calculate_headcount_multiplier(date, poverty_rate)`
     - Final headcount: `headcount = int(base * mult)`
     - Clamp headcount: `max(20, min(headcount, 800))`
     - Create HistoricalDistribution record
3. Batch commit every 1000 records for performance
4. Print progress every 10 sites

**Pitfall:** 90 days × 50 sites = 4,500 records. Batch commits are essential.

#### Function 6: `generate_warehouse_inventory(session, num_items: int, expiring_count: int)`

**Logic:**
1. Create list to track all items
2. For regular items (num_items - expiring_count):
   - Select random category from ITEM_CATEGORIES.keys()
   - Select random item name from that category's list
   - Generate quantity: `random.uniform(100, 5000)` with 2 decimals
   - Generate unit based on category:
     - produce/protein: 'lbs'
     - dairy: 'gallons' or 'lbs'
     - dry_goods: 'lbs' or 'cases'
     - frozen: 'lbs'
   - Received date: random date in past 30 days
   - Expiration date: received_date + random.randint(7, 90) days
3. For expiring items (expiring_count):
   - Same as above but:
   - Received date: 30-60 days ago
   - Expiration date: TODAY + random.randint(6, 72) HOURS (convert to date)
   - This ensures 3-5 items expire within 72 hours
4. Commit all items

**Pitfall:** Ensure expiring items have expiration_date in range [today, today+3 days].

#### Function 7: `generate_truck_fleet(session, num_trucks: int)`

**Logic:**
1. For i in range(1, num_trucks + 1):
   - truck_number: `f"TRUCK-{i:03d}"`
   - capacity_lbs: `random.randint(500, 800)`
   - status: 'active'
2. Commit all trucks

#### Function 8: `generate_volunteer_availability(session, start_date: date, end_date: date)`

**Logic:**
1. For each date from start_date to end_date:
   - Base count: 115 (midpoint of 80-150)
   - Add random variance: ±35
   - Day of week pattern:
     - Mon-Fri: no change
     - Sat: multiply by 0.7
     - Sun: multiply by 0.5
   - Final count: `max(80, min(volunteer_count, 150))`
2. Commit all records

#### Function 9: `seed_database()`

**Main orchestration logic:**
```python
1. Load environment variables
2. Get database engine
3. Initialize database (drop and recreate tables)
4. Get session
5. Print "Starting data generation..."
6. num_sites = random.randint(*NUM_SITES_RANGE)
7. Call generate_partner_sites(session, num_sites)
   - Print "Created {num_sites} partner sites"
8. Call generate_historical_distribution(session, sites, START_DATE, END_DATE)
   - Print "Created 90 days of historical distribution data"
9. num_inventory = random.randint(*NUM_INVENTORY_RANGE)
10. Call generate_warehouse_inventory(session, num_inventory, EXPIRING_SOON_COUNT)
    - Print "Created {num_inventory} inventory items ({EXPIRING_SOON_COUNT} expiring soon)"
11. Call generate_truck_fleet(session, NUM_TRUCKS)
    - Print "Created {NUM_TRUCKS} trucks"
12. Call generate_volunteer_availability(session, START_DATE, END_DATE)
    - Print "Created 90 days of volunteer availability data"
13. session.close()
14. Print "Data seeding complete!"

if __name__ == "__main__":
    seed_database()
```

---

## Data Structures

### ZIP Code Data Structure:
```python
{
    "zip": "44101",
    "lat": 41.5034,
    "lon": -81.6934,
    "county": "Cuyahoga",
    "poverty_rate": 0.28
}
```

### 6-County ZIP Code Distribution:
- Cuyahoga: 15-20 ZIPs (urban, higher population)
- Lake: 8-10 ZIPs
- Geauga: 6-8 ZIPs
- Ashtabula: 10-12 ZIPs
- Trumbull: 10-12 ZIPs
- Portage: 8-10 ZIPs
- **Total: ~60-70 ZIPs across all counties**

---

## Potential Pitfalls and Solutions

### Pitfall 1: Database Connection Issues
**Problem:** PostgreSQL not running or connection string incorrect.
**Solution:** 
- Validate DATABASE_URL format: `postgresql://user:password@host:port/database`
- Test connection before running seed script
- Provide clear error messages

### Pitfall 2: Memory Issues with Large Batch Inserts
**Problem:** 4,500+ historical distribution records may cause memory issues.
**Solution:**
- Use `session.bulk_insert_mappings()` instead of individual `session.add()`
- Commit every 1000 records
- Clear session after each batch: `session.expire_all()`

### Pitfall 3: Date Range Calculations
**Problem:** Off-by-one errors in date ranges.
**Solution:**
- Use inclusive date ranges: `start_date <= date <= end_date`
- Test with `timedelta` carefully
- Verify 90-day range produces exactly 90 days of data

### Pitfall 4: Foreign Key Constraint Violations
**Problem:** Historical distribution references non-existent site_id.
**Solution:**
- Generate and commit partner sites FIRST
- Store returned site objects in list
- Use site.id when creating historical records

### Pitfall 5: Duplicate Data on Re-runs
**Problem:** Running seed script multiple times creates duplicates.
**Solution:**
- `init_db()` drops all tables before recreating
- This ensures clean slate on each run
- Document this behavior in seed script comments

### Pitfall 6: Timezone Issues
**Problem:** Dates stored in wrong timezone.
**Solution:**
- Use `date` type for date-only fields
- Use `datetime.now()` for timestamps
- PostgreSQL will handle timezone based on server config

### Pitfall 7: Unrealistic Data Patterns
**Problem:** Generated data doesn't match real-world patterns.
**Solution:**
- Test multipliers independently
- Verify SNAP spikes occur on 1st and 15th
- Check that high-poverty ZIPs have consistently higher demand
- Sample and visualize generated data

### Pitfall 8: Expiring Items Not in Correct Date Range
**Problem:** Items expire outside 72-hour window.
**Solution:**
- Use hours for precise calculation: `expiration_date = today + timedelta(hours=random.randint(6, 72))`
- Validate after generation: query items with `expiration_date <= today + timedelta(days=3)`

### Pitfall 9: Path Issues in Imports
**Problem:** Python can't find db module.
**Solution:**
- Use `sys.path.append('..')` in seed.py
- Or run from backend directory: `python -m data.seed`
- Document correct execution path

### Pitfall 10: SQLAlchemy Session Management
**Problem:** Stale sessions or uncommitted data.
**Solution:**
- Always call `session.commit()` after batch operations
- Use try-except-finally blocks
- Close session in finally block

---

## Validation Steps

After running seed script, validate data:

```python
# Run these queries to verify
1. SELECT COUNT(*) FROM partner_sites;  # Should be 40-60
2. SELECT COUNT(DISTINCT zip_code) FROM partner_sites;  # Should span all 6 counties
3. SELECT COUNT(*) FROM historical_distribution;  # Should be sites × 90
4. SELECT COUNT(*) FROM warehouse_inventory;  # Should be 15-25
5. SELECT COUNT(*) FROM warehouse_inventory WHERE expiration_date <= CURRENT_DATE + INTERVAL '3 days';  # Should be 3-5
6. SELECT COUNT(*) FROM truck_fleet;  # Should be 5
7. SELECT COUNT(*) FROM volunteer_availability;  # Should be 90
8. SELECT AVG(headcount), MIN(headcount), MAX(headcount) FROM historical_distribution;  # Verify ranges
9. SELECT date, AVG(headcount) FROM historical_distribution WHERE EXTRACT(DAY FROM date) IN (1, 15) GROUP BY date ORDER BY date;  # Verify SNAP spikes
```

---

## Execution Order

1. Create `backend/data/zip_coordinates.py` with 60-70 real ZIP codes
2. Complete `backend/db.py` with all models and functions
3. Create `backend/.env` from `.env.example` with valid DATABASE_URL
4. Complete `backend/data/seed.py` with all generation functions
5. Run: `cd backend && python data/seed.py`
6. Validate data using queries above
7. Test SQLAlchemy CRUD operations

---

## Success Criteria

- [ ] All 5 tables created in PostgreSQL
- [ ] 40-60 partner sites spanning 6 counties
- [ ] 90 days × sites count of historical distribution records
- [ ] SNAP spikes visible on 1st and 15th of each month
- [ ] High-poverty ZIPs show higher average demand
- [ ] 3-5 inventory items expiring within 72 hours
- [ ] 5 trucks with varying capacities
- [ ] 90 days of volunteer data
- [ ] No database errors or constraint violations
- [ ] Script can be re-run cleanly (idempotent)
