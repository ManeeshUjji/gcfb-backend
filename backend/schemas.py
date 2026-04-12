from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class PartnerSiteBase(BaseModel):
    """Base schema for partner site information."""
    id: int
    name: str
    address: str
    zip_code: str
    latitude: float
    longitude: float
    program_type: str
    capacity_per_day: int
    operating_days: str

    class Config:
        from_attributes = True


class ZIPForecast(BaseModel):
    """Forecast for a single ZIP code."""
    zip_code: str
    predicted_headcount: int
    confidence_lower: int
    confidence_upper: int
    color_code: str = Field(..., description="green, yellow, or red based on demand threshold")
    num_sites: int


class ForecastResponse(BaseModel):
    """Response containing forecasts for multiple ZIPs."""
    date: date
    forecasts: List[ZIPForecast]


class ContributingFactor(BaseModel):
    """A factor contributing to demand prediction."""
    feature: str
    importance: float
    explanation: str


class DetailedForecast(BaseModel):
    """Detailed forecast for a single ZIP code."""
    zip_code: str
    date: date
    predicted_headcount: int
    confidence_interval: dict
    percent_change_vs_last_week: Optional[float] = None
    top_factors: List[ContributingFactor]
    partner_sites: List[PartnerSiteBase]


class RouteStop(BaseModel):
    """A single stop in a truck route."""
    site_id: int
    site_name: str
    zip_code: str
    latitude: float
    longitude: float
    predicted_demand: int
    quantity_lbs: int
    stop_order: int


class TruckRoute(BaseModel):
    """Complete route for a single truck."""
    truck_number: str
    stops: List[RouteStop]
    total_distance_miles: float
    estimated_time_hours: float
    total_load_lbs: int


class DispatchRequest(BaseModel):
    """Request to generate dispatch plan."""
    truck_count: int = Field(..., gt=0, description="Number of trucks available")
    volunteer_count: int = Field(..., ge=0, description="Number of volunteers available")
    date: Optional[date] = None


class DispatchResponse(BaseModel):
    """Response containing optimized dispatch plan."""
    date: date
    truck_routes: List[TruckRoute]
    total_distance_miles: float
    total_sites_served: int
    total_headcount_covered: int


class InventoryItem(BaseModel):
    """Warehouse inventory item."""
    id: int
    item_name: str
    category: str
    quantity: float
    unit: str
    expiration_date: date
    received_date: date
    days_until_expiration: int
    urgency: str = Field(..., description="red (<24hrs), orange (<72hrs)")

    class Config:
        from_attributes = True


class ExpiringInventoryResponse(BaseModel):
    """Response containing items expiring soon."""
    items: List[InventoryItem]
    total_count: int


class SiteMatch(BaseModel):
    """A suggested partner site for an expiring item."""
    site_id: int
    site_name: str
    zip_code: str
    address: str
    program_type: str
    distance_miles: float
    predicted_demand: int
    match_score: float
    explanation: str


class SiteMatchResponse(BaseModel):
    """Response containing top matched sites for an item."""
    item_id: int
    item_name: str
    suggested_sites: List[SiteMatch]


class AssignmentRequest(BaseModel):
    """Request to assign an item to a site in dispatch plan."""
    item_id: int
    site_id: int


class AssignmentResponse(BaseModel):
    """Response after adding assignment to dispatch plan."""
    success: bool
    message: str
    assignment: dict


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    ml_model_loaded: bool
    timestamp: datetime
    
    class Config:
        protected_namespaces = ()
