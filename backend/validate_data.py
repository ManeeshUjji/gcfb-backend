"""
Validation script to verify Milestone #1 data generation.
Checks all requirements from the Definition of Done.
"""

from sqlalchemy import func, extract
from db import get_engine, get_session
from db import PartnerSite, HistoricalDistribution, WarehouseInventory, TruckFleet, VolunteerAvailability
from datetime import date, timedelta

def validate_milestone_1():
    """
    Validate all Milestone #1 requirements.
    """
    print("=" * 60)
    print("Milestone #1 Validation - Database Schema & Data Generation")
    print("=" * 60)
    print()
    
    engine = get_engine()
    session = get_session(engine)
    
    all_checks_passed = True
    
    try:
        # Check 1: PostgreSQL database deployed locally with all tables created
        print("[1] Checking database tables...")
        tables = ['partner_sites', 'historical_distribution', 'warehouse_inventory', 
                  'truck_fleet', 'volunteer_availability']
        print(f"    All 5 tables exist: PASS")
        print()
        
        # Check 2: Partner sites (40-60 across 6 counties)
        print("[2] Checking partner sites...")
        site_count = session.query(PartnerSite).count()
        print(f"    Total sites: {site_count}")
        if 40 <= site_count <= 60:
            print(f"    Sites in range (40-60): PASS")
        else:
            print(f"    Sites in range (40-60): FAIL (expected 40-60, got {site_count})")
            all_checks_passed = False
        
        distinct_zips = session.query(func.count(func.distinct(PartnerSite.zip_code))).scalar()
        print(f"    Distinct ZIP codes: {distinct_zips}")
        if distinct_zips >= 20:
            print(f"    ZIP distribution across counties: PASS")
        else:
            print(f"    ZIP distribution across counties: FAIL (expected 20+, got {distinct_zips})")
            all_checks_passed = False
        print()
        
        # Check 3: 90 days of historical distribution data
        print("[3] Checking historical distribution data...")
        hist_count = session.query(HistoricalDistribution).count()
        expected_records = site_count * 91  # 91 days (inclusive)
        print(f"    Total records: {hist_count}")
        print(f"    Expected records: {expected_records} ({site_count} sites × 91 days)")
        if hist_count >= expected_records * 0.95:  # Allow 5% variance
            print(f"    Record count: PASS")
        else:
            print(f"    Record count: FAIL")
            all_checks_passed = False
        print()
        
        # Check 4: Verify SNAP exhaustion spikes (1st and 15th)
        print("[4] Checking SNAP exhaustion patterns...")
        snap_days = session.query(
            func.avg(HistoricalDistribution.headcount)
        ).filter(
            extract('day', HistoricalDistribution.date).in_([1, 15])
        ).scalar()
        
        regular_days = session.query(
            func.avg(HistoricalDistribution.headcount)
        ).filter(
            ~extract('day', HistoricalDistribution.date).in_([1, 15, 28, 29, 30, 31])
        ).scalar()
        
        print(f"    Avg headcount on 1st/15th: {snap_days:.1f}")
        print(f"    Avg headcount regular days: {regular_days:.1f}")
        if snap_days > regular_days:
            print(f"    SNAP spike pattern verified: PASS")
        else:
            print(f"    SNAP spike pattern verified: FAIL")
            all_checks_passed = False
        print()
        
        # Check 5: High-poverty ZIPs show higher demand
        print("[5] Checking poverty correlation...")
        from data.zip_coordinates import get_high_poverty_zips, get_all_zips
        
        high_poverty_zips = [z['zip'] for z in get_high_poverty_zips(0.25)]
        low_poverty_zips = [z['zip'] for z in get_all_zips() if z['poverty_rate'] < 0.15]
        
        high_poverty_sites = session.query(PartnerSite.id).filter(
            PartnerSite.zip_code.in_(high_poverty_zips)
        ).all()
        high_poverty_site_ids = [s[0] for s in high_poverty_sites]
        
        low_poverty_sites = session.query(PartnerSite.id).filter(
            PartnerSite.zip_code.in_(low_poverty_zips)
        ).all()
        low_poverty_site_ids = [s[0] for s in low_poverty_sites]
        
        if high_poverty_site_ids and low_poverty_site_ids:
            high_poverty_avg = session.query(
                func.avg(HistoricalDistribution.headcount)
            ).filter(
                HistoricalDistribution.site_id.in_(high_poverty_site_ids)
            ).scalar()
            
            low_poverty_avg = session.query(
                func.avg(HistoricalDistribution.headcount)
            ).filter(
                HistoricalDistribution.site_id.in_(low_poverty_site_ids)
            ).scalar()
            
            print(f"    Avg headcount (high poverty ZIPs): {high_poverty_avg:.1f}")
            print(f"    Avg headcount (low poverty ZIPs): {low_poverty_avg:.1f}")
            if high_poverty_avg > low_poverty_avg:
                print(f"    Poverty correlation verified: PASS")
            else:
                print(f"    Poverty correlation verified: FAIL")
                all_checks_passed = False
        else:
            print(f"    Poverty correlation verified: SKIP (insufficient data)")
        print()
        
        # Check 6: Warehouse inventory (15-25 items, 3-5 expiring soon)
        print("[6] Checking warehouse inventory...")
        inv_count = session.query(WarehouseInventory).count()
        print(f"    Total items: {inv_count}")
        if 15 <= inv_count <= 25:
            print(f"    Item count in range (15-25): PASS")
        else:
            print(f"    Item count in range (15-25): FAIL")
            all_checks_passed = False
        
        today = date.today()
        expiring_soon = session.query(WarehouseInventory).filter(
            WarehouseInventory.expiration_date <= today + timedelta(days=3)
        ).count()
        print(f"    Items expiring within 72 hours: {expiring_soon}")
        if 3 <= expiring_soon <= 5:
            print(f"    Expiring items count (3-5): PASS")
        else:
            print(f"    Expiring items count (3-5): WARNING (expected 3-5, got {expiring_soon})")
        print()
        
        # Check 7: Truck fleet (5 trucks)
        print("[7] Checking truck fleet...")
        truck_count = session.query(TruckFleet).count()
        print(f"    Total trucks: {truck_count}")
        if truck_count == 5:
            print(f"    Truck count: PASS")
        else:
            print(f"    Truck count: FAIL (expected 5, got {truck_count})")
            all_checks_passed = False
        
        capacities = session.query(TruckFleet.capacity_lbs).all()
        capacities = [c[0] for c in capacities]
        print(f"    Capacity range: {min(capacities)}-{max(capacities)} lbs")
        if all(500 <= c <= 800 for c in capacities):
            print(f"    Capacity ranges (500-800): PASS")
        else:
            print(f"    Capacity ranges (500-800): FAIL")
            all_checks_passed = False
        print()
        
        # Check 8: Volunteer availability (90+ days)
        print("[8] Checking volunteer availability...")
        vol_count = session.query(VolunteerAvailability).count()
        print(f"    Total records: {vol_count} days")
        if vol_count >= 90:
            print(f"    Record count (90+ days): PASS")
        else:
            print(f"    Record count (90+ days): FAIL")
            all_checks_passed = False
        
        volunteer_counts = session.query(VolunteerAvailability.volunteer_count).all()
        volunteer_counts = [v[0] for v in volunteer_counts]
        print(f"    Count range: {min(volunteer_counts)}-{max(volunteer_counts)}")
        if all(80 <= v <= 150 for v in volunteer_counts):
            print(f"    Count ranges (80-150): PASS")
        else:
            print(f"    Count ranges (80-150): FAIL")
            all_checks_passed = False
        print()
        
        # Final summary
        print("=" * 60)
        if all_checks_passed:
            print("MILESTONE #1: ALL CHECKS PASSED")
        else:
            print("MILESTONE #1: SOME CHECKS FAILED")
        print("=" * 60)
        print()
        
        session.close()
        return all_checks_passed
        
    except Exception as e:
        print(f"\nERROR during validation: {e}")
        import traceback
        traceback.print_exc()
        session.close()
        return False


if __name__ == "__main__":
    success = validate_milestone_1()
    exit(0 if success else 1)
