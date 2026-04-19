from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from db import get_db, PartnerSite
from schemas import PartnerSiteBase
from db_lazy_init import ensure_db_initialized

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sites",
    tags=["sites"]
)


@router.get("/", response_model=List[PartnerSiteBase])
async def get_all_sites(db: Session = Depends(get_db)):
    """
    Returns full partner site list with coordinates and program types.
    
    Returns all partner sites in the 6-county service area with their
    geographic coordinates for map visualization.
    """
    try:
        ensure_db_initialized()
        logger.info("Fetching all partner sites")
        
        sites = db.query(PartnerSite).all()
        
        result = [
            PartnerSiteBase(
                id=site.id,
                name=site.name,
                address=site.address,
                zip_code=site.zip_code,
                latitude=site.latitude,
                longitude=site.longitude,
                program_type=site.program_type,
                capacity_per_day=site.capacity_per_day,
                operating_days=site.operating_days
            )
            for site in sites
        ]
        
        logger.info(f"Retrieved {len(result)} partner sites")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching sites: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching sites: {str(e)}")


@router.get("/{zip_code}", response_model=List[PartnerSiteBase])
async def get_sites_by_zip(zip_code: str, db: Session = Depends(get_db)):
    """
    Returns partner sites within a specific ZIP code.
    
    Args:
        zip_code: ZIP code to filter by
        
    Returns list of partner sites in that ZIP code.
    """
    try:
        logger.info(f"Fetching sites for ZIP code {zip_code}")
        
        sites = db.query(PartnerSite).filter(
            PartnerSite.zip_code == zip_code
        ).all()
        
        if not sites:
            raise HTTPException(
                status_code=404,
                detail=f"No partner sites found in ZIP code {zip_code}"
            )
        
        result = [
            PartnerSiteBase(
                id=site.id,
                name=site.name,
                address=site.address,
                zip_code=site.zip_code,
                latitude=site.latitude,
                longitude=site.longitude,
                program_type=site.program_type,
                capacity_per_day=site.capacity_per_day,
                operating_days=site.operating_days
            )
            for site in sites
        ]
        
        logger.info(f"Retrieved {len(result)} sites in ZIP {zip_code}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sites by ZIP: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching sites: {str(e)}")
