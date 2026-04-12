"""
Data seeding script for GCFB dashboard.
Generates realistic simulated data for:
- Partner sites (40-60 across 6 counties)
- Historical distribution records (90 days)
- Warehouse inventory (15-25 items, 3-5 expiring soon)
- Truck fleet (5 trucks)
- Volunteer availability (daily counts)
"""

import random
import sys
import os
from datetime import datetime, timedelta, date
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import (
    get_engine, init_db, get_session,
    PartnerSite, HistoricalDistribution, WarehouseInventory,
    TruckFleet, VolunteerAvailability
)
from data.zip_coordinates import get_all_zips, get_random_zip, get_high_poverty_zips

# Date ranges
END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=90)

# Generation ranges
NUM_SITES_RANGE = (40, 60)
NUM_INVENTORY_RANGE = (15, 25)
NUM_TRUCKS = 5
EXPIRING_SOON_COUNT = 5

# Program types
PROGRAM_TYPES = ['pantry', 'senior', 'kids_cafe', 'mobile', 'shelter']

# Item categories
ITEM_CATEGORIES = {
    'produce': ['Apples', 'Bananas', 'Carrots', 'Lettuce', 'Tomatoes', 'Potatoes', 'Onions', 'Oranges', 'Broccoli'],
    'dairy': ['Milk', 'Cheese', 'Yogurt', 'Butter', 'Eggs'],
    'dry_goods': ['Rice', 'Pasta', 'Canned Beans', 'Canned Corn', 'Cereal', 'Oatmeal', 'Flour', 'Sugar'],
    'protein': ['Chicken', 'Ground Beef', 'Pork', 'Canned Tuna', 'Peanut Butter', 'Salmon'],
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


def generate_partner_sites(session, num_sites: int) -> List[PartnerSite]:
    """
    Generate 40-60 simulated partner sites across 6 counties.
    
    Args:
        session: SQLAlchemy session
        num_sites: Number of sites to generate
        
    Returns:
        List of created PartnerSite objects
    """
    print(f"Generating {num_sites} partner sites...")
    
    all_zips = get_all_zips()
    sites = []
    
    for i in range(num_sites):
        zip_data = random.choice(all_zips)
        program_type = random.choice(PROGRAM_TYPES)
        
        site = PartnerSite(
            name=f"{program_type.replace('_', ' ').title()} at {zip_data['zip']}",
            address=f"{random.randint(100, 9999)} Main St, ZIP {zip_data['zip']}",
            zip_code=zip_data['zip'],
            latitude=zip_data['lat'],
            longitude=zip_data['lon'],
            program_type=program_type,
            capacity_per_day=random.randint(50, 500),
            operating_days=random.choice(OPERATING_PATTERNS)
        )
        sites.append(site)
    
    session.add_all(sites)
    session.commit()
    
    print(f"Created {len(sites)} partner sites")
    return sites


def calculate_headcount_multiplier(date_obj: date, zip_poverty_rate: float) -> float:
    """
    Calculate demand multiplier based on date patterns and poverty rate.
    
    Args:
        date_obj: Date to calculate for
        zip_poverty_rate: Poverty rate for the ZIP code (0.0 to 1.0)
        
    Returns:
        Multiplier value to apply to base headcount
    """
    multiplier = 1.0
    
    # SNAP exhaustion pattern
    day = date_obj.day
    if day in [1, 2]:
        multiplier *= 1.4
    elif day in [15, 16]:
        multiplier *= 1.3
    elif day >= 28:
        multiplier *= 1.2
    
    # Seasonal pattern
    month = date_obj.month
    if month in [12, 1, 2]:  # Winter
        multiplier *= 1.3
    elif month in [11, 3]:  # Late fall/early spring
        multiplier *= 1.15
    elif month in [6, 7, 8]:  # Summer
        multiplier *= 0.9
    
    # Weekend pattern
    weekday = date_obj.weekday()
    if weekday in [5, 6]:  # Saturday, Sunday
        multiplier *= 0.6
    
    # Poverty correlation
    if zip_poverty_rate > 0.25:
        multiplier *= 1.3
    elif zip_poverty_rate > 0.20:
        multiplier *= 1.15
    
    return multiplier


def calculate_base_headcount(program_type: str, capacity: int) -> int:
    """
    Calculate base headcount for a site based on program type and capacity.
    
    Args:
        program_type: Type of program
        capacity: Site capacity per day
        
    Returns:
        Base headcount with random variance
    """
    utilization = {
        'pantry': 0.75,
        'senior': 0.65,
        'kids_cafe': 0.80,
        'mobile': 0.70,
        'shelter': 0.85
    }
    
    base = int(capacity * utilization[program_type])
    variance = random.uniform(0.85, 1.15)
    return int(base * variance)


def generate_weather_data(date_obj: date) -> Tuple[float, float]:
    """
    Generate simulated weather data for Cleveland area.
    
    Args:
        date_obj: Date to generate weather for
        
    Returns:
        Tuple of (temperature_f, precipitation_inches)
    """
    month = date_obj.month
    
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
    
    return (round(temp, 2), round(precip, 2))


def generate_historical_distribution(session, sites: List[PartnerSite], start_date: date, end_date: date):
    """
    Generate 90 days of distribution records with realistic patterns.
    
    Args:
        session: SQLAlchemy session
        sites: List of PartnerSite objects
        start_date: Start date for historical data
        end_date: End date for historical data
    """
    print(f"Generating historical distribution data from {start_date} to {end_date}...")
    
    zip_poverty = {z['zip']: z['poverty_rate'] for z in get_all_zips()}
    
    records = []
    current_date = start_date
    
    for site_idx, site in enumerate(sites):
        poverty_rate = zip_poverty.get(site.zip_code, 0.15)
        
        current_date = start_date
        while current_date <= end_date:
            temp, precip = generate_weather_data(current_date)
            base = calculate_base_headcount(site.program_type, site.capacity_per_day)
            mult = calculate_headcount_multiplier(current_date, poverty_rate)
            headcount = int(base * mult)
            headcount = max(20, min(headcount, 800))
            
            record = HistoricalDistribution(
                site_id=site.id,
                date=current_date,
                headcount=headcount,
                program_type=site.program_type,
                temperature_f=temp,
                precipitation_inches=precip
            )
            records.append(record)
            
            if len(records) >= 1000:
                session.bulk_save_objects(records)
                session.commit()
                records = []
            
            current_date += timedelta(days=1)
        
        if (site_idx + 1) % 10 == 0:
            print(f"  Processed {site_idx + 1}/{len(sites)} sites...")
    
    if records:
        session.bulk_save_objects(records)
        session.commit()
    
    print(f"Created historical distribution records for {len(sites)} sites over 90 days")


def generate_warehouse_inventory(session, num_items: int, expiring_count: int):
    """
    Generate 15-25 warehouse items with 3-5 expiring soon.
    
    Args:
        session: SQLAlchemy session
        num_items: Total number of items to generate
        expiring_count: Number of items that should expire within 72 hours
    """
    print(f"Generating {num_items} warehouse inventory items ({expiring_count} expiring soon)...")
    
    items = []
    today = date.today()
    
    regular_items = num_items - expiring_count
    
    for i in range(regular_items):
        category = random.choice(list(ITEM_CATEGORIES.keys()))
        item_name = random.choice(ITEM_CATEGORIES[category])
        
        if category in ['produce', 'protein']:
            unit = 'lbs'
        elif category == 'dairy':
            unit = random.choice(['gallons', 'lbs'])
        elif category == 'dry_goods':
            unit = random.choice(['lbs', 'cases'])
        else:  # frozen
            unit = 'lbs'
        
        received_date = today - timedelta(days=random.randint(1, 30))
        expiration_date = received_date + timedelta(days=random.randint(7, 90))
        
        item = WarehouseInventory(
            item_name=f"{item_name} - Batch {i+1}",
            category=category,
            quantity=round(random.uniform(100, 5000), 2),
            unit=unit,
            received_date=received_date,
            expiration_date=expiration_date
        )
        items.append(item)
    
    for i in range(expiring_count):
        category = random.choice(list(ITEM_CATEGORIES.keys()))
        item_name = random.choice(ITEM_CATEGORIES[category])
        
        if category in ['produce', 'protein']:
            unit = 'lbs'
        elif category == 'dairy':
            unit = random.choice(['gallons', 'lbs'])
        elif category == 'dry_goods':
            unit = random.choice(['lbs', 'cases'])
        else:
            unit = 'lbs'
        
        received_date = today - timedelta(days=random.randint(30, 60))
        hours_until_expiry = random.randint(6, 72)
        expiration_datetime = datetime.now() + timedelta(hours=hours_until_expiry)
        expiration_date = expiration_datetime.date()
        
        item = WarehouseInventory(
            item_name=f"{item_name} - Expiring Soon {i+1}",
            category=category,
            quantity=round(random.uniform(50, 500), 2),
            unit=unit,
            received_date=received_date,
            expiration_date=expiration_date
        )
        items.append(item)
    
    session.add_all(items)
    session.commit()
    
    print(f"Created {len(items)} warehouse inventory items")


def generate_truck_fleet(session, num_trucks: int):
    """
    Generate truck fleet with varying capacity.
    
    Args:
        session: SQLAlchemy session
        num_trucks: Number of trucks to generate
    """
    print(f"Generating {num_trucks} trucks...")
    
    trucks = []
    for i in range(1, num_trucks + 1):
        truck = TruckFleet(
            truck_number=f"TRUCK-{i:03d}",
            capacity_lbs=random.randint(500, 800),
            status='active'
        )
        trucks.append(truck)
    
    session.add_all(trucks)
    session.commit()
    
    print(f"Created {len(trucks)} trucks")


def generate_volunteer_availability(session, start_date: date, end_date: date):
    """
    Generate daily volunteer availability counts.
    
    Args:
        session: SQLAlchemy session
        start_date: Start date
        end_date: End date
    """
    print(f"Generating volunteer availability from {start_date} to {end_date}...")
    
    volunteers = []
    current_date = start_date
    
    while current_date <= end_date:
        base_count = 115
        variance = random.randint(-35, 35)
        count = base_count + variance
        
        weekday = current_date.weekday()
        if weekday == 5:  # Saturday
            count = int(count * 0.7)
        elif weekday == 6:  # Sunday
            count = int(count * 0.5)
        
        count = max(80, min(count, 150))
        
        volunteer = VolunteerAvailability(
            date=current_date,
            volunteer_count=count
        )
        volunteers.append(volunteer)
        
        current_date += timedelta(days=1)
    
    session.add_all(volunteers)
    session.commit()
    
    print(f"Created {len(volunteers)} volunteer availability records")


def seed_database():
    """Main function to seed all data into database."""
    print("=" * 60)
    print("GCFB Data Seeding Script")
    print("=" * 60)
    print()
    
    try:
        print("Loading environment variables...")
        engine = get_engine()
        
        print("Initializing database (dropping and recreating tables)...")
        init_db(engine)
        
        print("Creating database session...")
        session = get_session(engine)
        
        print("\nStarting data generation...")
        print("-" * 60)
        
        num_sites = random.randint(*NUM_SITES_RANGE)
        sites = generate_partner_sites(session, num_sites)
        
        print()
        generate_historical_distribution(session, sites, START_DATE, END_DATE)
        
        print()
        num_inventory = random.randint(*NUM_INVENTORY_RANGE)
        generate_warehouse_inventory(session, num_inventory, EXPIRING_SOON_COUNT)
        
        print()
        generate_truck_fleet(session, NUM_TRUCKS)
        
        print()
        generate_volunteer_availability(session, START_DATE, END_DATE)
        
        print()
        print("-" * 60)
        print("Data seeding complete!")
        print("=" * 60)
        
        print("\nSummary:")
        print(f"  Partner Sites: {num_sites}")
        print(f"  Historical Records: {num_sites * 91} (90 days)")
        print(f"  Warehouse Items: {num_inventory} ({EXPIRING_SOON_COUNT} expiring soon)")
        print(f"  Trucks: {NUM_TRUCKS}")
        print(f"  Volunteer Records: 91 days")
        print()
        
        session.close()
        
    except Exception as e:
        print(f"\nERROR during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    seed_database()
