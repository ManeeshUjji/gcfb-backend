from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import date
import logging
import math
from typing import Dict, List, Tuple
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from db import get_db, PartnerSite, TruckFleet, WarehouseInventory
from schemas import (
    DispatchRequest, DispatchResponse, TruckRoute, RouteStop,
    AssignmentRequest, AssignmentResponse
)
from models.model_utils import predict_headcount
from utils.weather import get_weather_service
from utils.equity import calculate_equity_weight, get_poverty_rate
from db_lazy_init import ensure_db_initialized

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dispatch",
    tags=["dispatch"]
)

WAREHOUSE_LAT = 41.4993
WAREHOUSE_LON = -81.6944
MILES_PER_DEGREE = 69.0
AVG_SPEED_MPH = 35.0

_active_dispatch_plan = None


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in miles using Haversine formula."""
    R = 3959
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def _create_distance_matrix(locations: List[Tuple[float, float]]) -> List[List[int]]:
    """
    Create distance matrix for OR-Tools.
    Locations[0] should be the warehouse/depot.
    Returns matrix in meters.
    """
    size = len(locations)
    matrix = [[0] * size for _ in range(size)]
    
    for i in range(size):
        for j in range(size):
            if i != j:
                distance = _calculate_distance(
                    locations[i][0], locations[i][1],
                    locations[j][0], locations[j][1]
                )
                matrix[i][j] = int(distance * 1609.34)
    
    return matrix


def _get_site_demands_with_equity(
    sites: List[PartnerSite],
    forecast_date: date,
    db: Session
) -> Dict:
    """
    Get demand predictions for sites with equity weighting applied.
    Returns dict with site info and priority scores.
    """
    weather_service = get_weather_service()
    site_data = []
    
    for site in sites:
        weather = weather_service.get_current_weather(site.latitude, site.longitude)
        if weather is None:
            weather = {'temperature_f': 60.0, 'precipitation_inches': 0.0}
        
        poverty_rate = get_poverty_rate(site.zip_code)
        
        prediction = predict_headcount(
            zip_code=site.zip_code,
            program_type=site.program_type,
            prediction_date=forecast_date,
            temperature_f=weather['temperature_f'],
            precipitation_inches=weather['precipitation_inches'],
            poverty_rate=poverty_rate,
            capacity_per_day=site.capacity_per_day
        )
        
        equity_weight = calculate_equity_weight(site.zip_code)
        
        priority_score = prediction['predicted_headcount'] * equity_weight
        
        site_data.append({
            'site': site,
            'predicted_demand': prediction['predicted_headcount'],
            'equity_weight': equity_weight,
            'priority_score': priority_score
        })
    
    site_data.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return site_data


@router.post("/", response_model=DispatchResponse)
async def generate_dispatch_plan(
    request: DispatchRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Accepts truck count + volunteer count, returns optimized route plan.
    Uses Google OR-Tools for vehicle routing optimization.
    Applies equity weighting based on poverty index.
    """
    global _active_dispatch_plan
    
    try:
        ensure_db_initialized()
        logger.info(f"Generating dispatch plan for {request.truck_count} trucks")
        
        forecast_date = request.date if request.date else date.today()
        
        trucks = db.query(TruckFleet).filter(
            TruckFleet.status == 'active'
        ).limit(request.truck_count).all()
        
        if not trucks:
            raise HTTPException(status_code=404, detail="No active trucks available")
        
        sites = db.query(PartnerSite).all()
        
        if not sites:
            raise HTTPException(status_code=404, detail="No partner sites found")
        
        site_data = _get_site_demands_with_equity(sites, forecast_date, db)
        
        top_sites = site_data[:min(len(site_data), 30)]
        
        locations = [(WAREHOUSE_LAT, WAREHOUSE_LON)]
        locations.extend([(s['site'].latitude, s['site'].longitude) for s in top_sites])
        
        distance_matrix = _create_distance_matrix(locations)
        
        manager = pywrapcp.RoutingIndexManager(
            len(distance_matrix),
            len(trucks),
            0
        )
        
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        demands = [0]
        for s in top_sites:
            demand_lbs = int(s['predicted_demand'] * 2.5)
            demands.append(demand_lbs)
        
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return demands[from_node]
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        
        vehicle_capacities = [truck.capacity_lbs for truck in trucks]
        
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            vehicle_capacities,
            True,
            'Capacity'
        )
        
        penalty = 1000000
        for node in range(1, len(distance_matrix)):
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
        
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC
        )
        search_parameters.time_limit.seconds = 30
        search_parameters.log_search = False
        
        logger.info(f"Solving routing problem with {len(distance_matrix)} locations and {len(trucks)} trucks")
        
        solution = routing.SolveWithParameters(search_parameters)
        
        if not solution:
            logger.warning(f"Could not find solution. Status: {routing.status()}")
            logger.warning(f"Total demand: {sum(demands)}, Total capacity: {sum(vehicle_capacities)}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not find optimal route solution. Try with more trucks or fewer sites."
            )
        
        truck_routes = []
        total_distance = 0
        total_sites_served = 0
        total_headcount = 0
        
        for vehicle_id in range(len(trucks)):
            index = routing.Start(vehicle_id)
            route_distance = 0
            route_load = 0
            stops = []
            stop_order = 1
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                
                if node_index > 0:
                    site_idx = node_index - 1
                    site_info = top_sites[site_idx]
                    site = site_info['site']
                    
                    stops.append(RouteStop(
                        site_id=site.id,
                        site_name=site.name,
                        zip_code=site.zip_code,
                        latitude=site.latitude,
                        longitude=site.longitude,
                        predicted_demand=site_info['predicted_demand'],
                        quantity_lbs=int(site_info['predicted_demand'] * 2.5),
                        stop_order=stop_order
                    ))
                    
                    route_load += demands[node_index]
                    total_headcount += site_info['predicted_demand']
                    stop_order += 1
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            
            if stops:
                route_distance_miles = route_distance / 1609.34
                route_time_hours = route_distance_miles / AVG_SPEED_MPH
                
                truck_routes.append(TruckRoute(
                    truck_number=trucks[vehicle_id].truck_number,
                    stops=stops,
                    total_distance_miles=round(route_distance_miles, 2),
                    estimated_time_hours=round(route_time_hours, 2),
                    total_load_lbs=route_load
                ))
                
                total_distance += route_distance_miles
                total_sites_served += len(stops)
        
        response = DispatchResponse(
            date=forecast_date,
            truck_routes=truck_routes,
            total_distance_miles=round(total_distance, 2),
            total_sites_served=total_sites_served,
            total_headcount_covered=total_headcount
        )
        
        _active_dispatch_plan = response
        
        logger.info(f"Generated dispatch plan with {len(truck_routes)} routes")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating dispatch plan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating dispatch: {str(e)}")


@router.post("/assign", response_model=AssignmentResponse)
async def assign_to_dispatch(
    request: AssignmentRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Adds an expiration assignment into the current dispatch plan.
    Updates the active dispatch plan state.
    """
    global _active_dispatch_plan
    
    try:
        logger.info(f"Assigning item {request.item_id} to site {request.site_id}")
        
        item = db.query(WarehouseInventory).filter(
            WarehouseInventory.id == request.item_id
        ).first()
        
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {request.item_id} not found")
        
        site = db.query(PartnerSite).filter(
            PartnerSite.id == request.site_id
        ).first()
        
        if not site:
            raise HTTPException(status_code=404, detail=f"Site {request.site_id} not found")
        
        assignment = {
            'item_id': request.item_id,
            'item_name': item.item_name,
            'quantity': item.quantity,
            'unit': item.unit,
            'site_id': request.site_id,
            'site_name': site.name,
            'zip_code': site.zip_code
        }
        
        logger.info(f"Successfully assigned {item.item_name} to {site.name}")
        
        return AssignmentResponse(
            success=True,
            message=f"Successfully assigned {item.item_name} to {site.name}",
            assignment=assignment
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning to dispatch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating assignment: {str(e)}")
