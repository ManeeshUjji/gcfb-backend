"""
Lazy database initialization helper.
Initializes and seeds database on first use rather than at startup.
"""
import logging
from threading import Lock

logger = logging.getLogger(__name__)

_db_initialized = False
_init_lock = Lock()


def ensure_db_initialized():
    """
    Ensure database is initialized and seeded.
    Thread-safe lazy initialization on first call.
    """
    global _db_initialized
    
    if _db_initialized:
        return
    
    with _init_lock:
        # Double-check after acquiring lock
        if _db_initialized:
            return
            
        logger.info("Performing lazy database initialization...")
        
        try:
            from db import get_engine, init_db, get_session, PartnerSite
            from data.seed import (
                generate_partner_sites, generate_historical_distribution,
                generate_warehouse_inventory, generate_truck_fleet,
                generate_volunteer_availability, NUM_TRUCKS, EXPIRING_SOON_COUNT,
                START_DATE, END_DATE
            )
            
            engine = get_engine()
            init_db(engine)
            session = get_session(engine)
            
            # Check if already seeded
            if session.query(PartnerSite).count() > 0:
                logger.info("Database already contains data")
                session.close()
                _db_initialized = True
                return
            
            # Quick seeding with minimal data
            logger.info("Seeding database (this may take 10-15 seconds)...")
            sites = generate_partner_sites(session, 30)  # Reduced to 30 sites
            generate_historical_distribution(session, sites, START_DATE, END_DATE)
            generate_warehouse_inventory(session, 15, EXPIRING_SOON_COUNT)
            generate_truck_fleet(session, NUM_TRUCKS)
            generate_volunteer_availability(session, START_DATE, END_DATE)
            
            session.close()
            _db_initialized = True
            logger.info("Database initialized and seeded successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}", exc_info=True)
            raise
