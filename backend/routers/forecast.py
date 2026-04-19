from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import Optional
import logging

from db import get_db, PartnerSite, HistoricalDistribution
from schemas import ForecastResponse, ZIPForecast, DetailedForecast, ContributingFactor, PartnerSiteBase
from models.model_utils import predict_headcount, get_top_factors
from utils.weather import get_weather_service
from utils.equity import get_poverty_rate
from db_lazy_init import ensure_db_initialized

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/forecast",
    tags=["forecast"]
)


def _get_forecast_date(date_param: str) -> date:
    """Parse date parameter and return date object."""
    if date_param == "today":
        return date.today()
    elif date_param == "tomorrow":
        return date.today() + timedelta(days=1)
    elif date_param == "week":
        return date.today()
    else:
        try:
            return date.fromisoformat(date_param)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use 'today', 'tomorrow', 'week', or YYYY-MM-DD")


def _get_color_code(predicted_headcount: int, capacity: int) -> str:
    """
    Determine color code based on demand vs capacity.
    - green: <70% capacity
    - yellow: 70-90% capacity
    - red: >90% capacity
    """
    utilization = predicted_headcount / capacity if capacity > 0 else 0
    
    if utilization < 0.7:
        return "green"
    elif utilization < 0.9:
        return "yellow"
    else:
        return "red"


@router.get("/", response_model=ForecastResponse)
async def get_forecast(
    date_param: str = Query("today", alias="date", description="Date for forecast: 'today', 'tomorrow', 'week', or YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Returns predicted demand per ZIP for specified date range.
    
    Query params:
    - date: 'today', 'tomorrow', 'week', or specific date in YYYY-MM-DD format
    
    Returns ZIP-level forecasts with color coding.
    """
    try:
        ensure_db_initialized()
        forecast_date = _get_forecast_date(date_param)
        logger.info(f"Generating forecast for {forecast_date}")
        
        sites = db.query(PartnerSite).all()
        
        weather_service = get_weather_service()
        
        zip_aggregates = {}
        
        for site in sites:
            zip_code = site.zip_code
            
            if zip_code not in zip_aggregates:
                zip_aggregates[zip_code] = {
                    'sites': [],
                    'total_predicted': 0,
                    'total_capacity': 0,
                    'predictions': []
                }
            
            weather = weather_service.get_current_weather(site.latitude, site.longitude)
            if weather is None:
                weather = {
                    'temperature_f': 60.0,
                    'precipitation_inches': 0.0
                }
            
            poverty_rate = get_poverty_rate(zip_code)
            
            prediction = predict_headcount(
                zip_code=zip_code,
                program_type=site.program_type,
                prediction_date=forecast_date,
                temperature_f=weather['temperature_f'],
                precipitation_inches=weather['precipitation_inches'],
                poverty_rate=poverty_rate,
                capacity_per_day=site.capacity_per_day
            )
            
            zip_aggregates[zip_code]['sites'].append(site)
            zip_aggregates[zip_code]['total_predicted'] += prediction['predicted_headcount']
            zip_aggregates[zip_code]['total_capacity'] += site.capacity_per_day
            zip_aggregates[zip_code]['predictions'].append(prediction)
        
        forecasts = []
        for zip_code, data in zip_aggregates.items():
            avg_lower = sum(p['confidence_interval']['lower'] for p in data['predictions']) // len(data['predictions'])
            avg_upper = sum(p['confidence_interval']['upper'] for p in data['predictions']) // len(data['predictions'])
            
            forecasts.append(ZIPForecast(
                zip_code=zip_code,
                predicted_headcount=data['total_predicted'],
                confidence_lower=avg_lower * len(data['sites']),
                confidence_upper=avg_upper * len(data['sites']),
                color_code=_get_color_code(data['total_predicted'], data['total_capacity']),
                num_sites=len(data['sites'])
            ))
        
        logger.info(f"Generated forecast for {len(forecasts)} ZIP codes")
        
        return ForecastResponse(
            date=forecast_date,
            forecasts=sorted(forecasts, key=lambda x: x.predicted_headcount, reverse=True)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")


@router.get("/{zip_code}", response_model=DetailedForecast)
async def get_forecast_detail(
    zip_code: str,
    date_param: str = Query("today", alias="date", description="Date for forecast"),
    db: Session = Depends(get_db)
):
    """
    Returns detailed forecast for a single ZIP including:
    - Predicted headcount range
    - % change vs same period last week
    - Top 3 contributing factors
    - List of partner sites in that ZIP
    """
    try:
        ensure_db_initialized()
        forecast_date = _get_forecast_date(date_param)
        logger.info(f"Generating detailed forecast for ZIP {zip_code} on {forecast_date}")
        
        sites = db.query(PartnerSite).filter(PartnerSite.zip_code == zip_code).all()
        
        if not sites:
            raise HTTPException(status_code=404, detail=f"No partner sites found in ZIP code {zip_code}")
        
        weather_service = get_weather_service()
        sample_site = sites[0]
        weather = weather_service.get_current_weather(sample_site.latitude, sample_site.longitude)
        
        if weather is None:
            weather = {'temperature_f': 60.0, 'precipitation_inches': 0.0}
        
        poverty_rate = get_poverty_rate(zip_code)
        
        total_predicted = 0
        all_confidence_intervals = []
        
        for site in sites:
            prediction = predict_headcount(
                zip_code=zip_code,
                program_type=site.program_type,
                prediction_date=forecast_date,
                temperature_f=weather['temperature_f'],
                precipitation_inches=weather['precipitation_inches'],
                poverty_rate=poverty_rate,
                capacity_per_day=site.capacity_per_day
            )
            
            total_predicted += prediction['predicted_headcount']
            all_confidence_intervals.append(prediction['confidence_interval'])
        
        avg_confidence = {
            'lower': sum(ci['lower'] for ci in all_confidence_intervals),
            'upper': sum(ci['upper'] for ci in all_confidence_intervals)
        }
        
        last_week_date = forecast_date - timedelta(days=7)
        last_week_data = db.query(
            func.sum(HistoricalDistribution.headcount).label('total')
        ).join(
            PartnerSite,
            HistoricalDistribution.site_id == PartnerSite.id
        ).filter(
            PartnerSite.zip_code == zip_code,
            HistoricalDistribution.date == last_week_date
        ).first()
        
        percent_change = None
        if last_week_data and last_week_data.total:
            percent_change = ((total_predicted - last_week_data.total) / last_week_data.total) * 100
        
        top_factors = get_top_factors(zip_code, forecast_date, poverty_rate, n=3)
        contributing_factors = [
            ContributingFactor(
                feature=f['feature'],
                importance=f['importance'],
                explanation=f['explanation']
            )
            for f in top_factors
        ]
        
        partner_sites_data = [
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
        
        return DetailedForecast(
            zip_code=zip_code,
            date=forecast_date,
            predicted_headcount=total_predicted,
            confidence_interval=avg_confidence,
            percent_change_vs_last_week=percent_change,
            top_factors=contributing_factors,
            partner_sites=partner_sites_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating detailed forecast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating detailed forecast: {str(e)}")
