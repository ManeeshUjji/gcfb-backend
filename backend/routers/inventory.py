from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
import logging
import math

from db import get_db, WarehouseInventory, PartnerSite
from schemas import ExpiringInventoryResponse, InventoryItem, SiteMatchResponse, SiteMatch
from models.model_utils import predict_headcount
from utils.weather import get_weather_service
from utils.equity import get_poverty_rate
from db_lazy_init import ensure_db_initialized

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

WAREHOUSE_LAT = 41.4993
WAREHOUSE_LON = -81.6944


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    Returns distance in miles.
    """
    R = 3959
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def _get_urgency_level(days_until_expiration: int) -> str:
    """Determine urgency level based on days remaining."""
    if days_until_expiration < 1:
        return "red"
    elif days_until_expiration <= 3:
        return "orange"
    else:
        return "yellow"


@router.get("/expiring", response_model=ExpiringInventoryResponse)
async def get_expiring_inventory(db: Session = Depends(get_db)):
    """
    Returns items expiring within 72 hours.
    Includes color-coded urgency (red < 24hrs, orange < 72hrs).
    """
    try:
        ensure_db_initialized()
        logger.info("Fetching expiring inventory items")
        
        expiration_threshold = date.today() + timedelta(days=3)
        
        items = db.query(WarehouseInventory).filter(
            WarehouseInventory.expiration_date <= expiration_threshold
        ).order_by(
            WarehouseInventory.expiration_date
        ).all()
        
        result_items = []
        for item in items:
            days_until_exp = (item.expiration_date - date.today()).days
            
            result_items.append(InventoryItem(
                id=item.id,
                item_name=item.item_name,
                category=item.category,
                quantity=item.quantity,
                unit=item.unit,
                expiration_date=item.expiration_date,
                received_date=item.received_date,
                days_until_expiration=days_until_exp,
                urgency=_get_urgency_level(days_until_exp)
            ))
        
        logger.info(f"Found {len(result_items)} items expiring within 72 hours")
        
        return ExpiringInventoryResponse(
            items=result_items,
            total_count=len(result_items)
        )
        
    except Exception as e:
        logger.error(f"Error fetching expiring inventory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching inventory: {str(e)}")


@router.get("/expiring/{item_id}/sites", response_model=SiteMatchResponse)
async def get_suggested_sites(item_id: int, db: Session = Depends(get_db)):
    """
    Returns top 3 suggested partner sites for an expiring item.
    Ranked by: proximity + program compatibility + capacity.
    Uses fast distance-based scoring (no ML predictions for speed).
    """
    try:
        ensure_db_initialized()
        logger.info(f"Finding suggested sites for item {item_id}")
        
        item = db.query(WarehouseInventory).filter(
            WarehouseInventory.id == item_id
        ).first()
        
        if not item:
            raise HTTPException(status_code=404, detail=f"Inventory item {item_id} not found")
        
        sites = db.query(PartnerSite).all()
        
        if not sites:
            raise HTTPException(status_code=404, detail="No partner sites found")
        
        forecast_date = date.today()
        site_scores = []
        
        for site in sites:
            distance = _calculate_distance(
                WAREHOUSE_LAT, WAREHOUSE_LON,
                site.latitude, site.longitude
            )
            
            poverty_rate = get_poverty_rate(site.zip_code)
            
            estimated_demand = int(site.capacity_per_day * 0.75 * (1 + poverty_rate))
            
            current_fill_rate = estimated_demand / site.capacity_per_day if site.capacity_per_day > 0 else 0
            
            distance_score = 1 / (1 + distance / 10)
            
            program_priority = {
                'pantry': 1.0,
                'senior': 0.9,
                'kids_cafe': 0.8,
                'mobile': 1.0,
                'shelter': 1.0
            }.get(site.program_type, 0.8)
            
            capacity_score = 1 - current_fill_rate
            
            match_score = (
                distance_score * 0.5 +
                program_priority * 0.3 +
                capacity_score * 0.2
            )
            
            explanation = _generate_match_explanation(
                distance, estimated_demand, current_fill_rate
            )
            
            site_scores.append({
                'site': site,
                'distance': distance,
                'predicted_demand': estimated_demand,
                'match_score': match_score,
                'explanation': explanation
            })
        
        site_scores.sort(key=lambda x: x['match_score'], reverse=True)
        top_3 = site_scores[:3]
        
        suggested_sites = [
            SiteMatch(
                site_id=s['site'].id,
                site_name=s['site'].name,
                zip_code=s['site'].zip_code,
                address=s['site'].address,
                program_type=s['site'].program_type,
                distance_miles=round(s['distance'], 2),
                predicted_demand=s['predicted_demand'],
                match_score=round(s['match_score'], 3),
                explanation=s['explanation']
            )
            for s in top_3
        ]
        
        logger.info(f"Found {len(suggested_sites)} suggested sites for item {item_id}")
        
        return SiteMatchResponse(
            item_id=item_id,
            item_name=item.item_name,
            suggested_sites=suggested_sites
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding suggested sites: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error finding sites: {str(e)}")


def _generate_match_explanation(distance: float, demand: int, fill_rate: float) -> str:
    """Generate human-readable explanation for match score."""
    parts = []
    
    if distance < 10:
        parts.append("nearby location")
    elif distance < 20:
        parts.append("moderate distance")
    else:
        parts.append("longer distance")
    
    if demand > 200:
        parts.append("high demand")
    elif demand > 100:
        parts.append("moderate demand")
    else:
        parts.append("lower demand")
    
    if fill_rate < 0.7:
        parts.append("available capacity")
    elif fill_rate < 0.9:
        parts.append("near capacity")
    else:
        parts.append("at capacity")
    
    return f"Good match: {', '.join(parts)}"
