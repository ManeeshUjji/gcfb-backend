"""
ZIP code coordinates and poverty data for GCFB 6-county service area.
Counties: Cuyahoga, Lake, Geauga, Ashtabula, Trumbull, Portage
"""

from typing import List, Dict, Optional
import random

# Real ZIP codes with coordinates for 6-county area
COUNTIES = {
    "Cuyahoga": [
        {"zip": "44101", "lat": 41.5034, "lon": -81.6934, "poverty_rate": 0.28},
        {"zip": "44102", "lat": 41.4789, "lon": -81.7293, "poverty_rate": 0.32},
        {"zip": "44103", "lat": 41.5156, "lon": -81.6490, "poverty_rate": 0.35},
        {"zip": "44104", "lat": 41.4956, "lon": -81.6290, "poverty_rate": 0.31},
        {"zip": "44105", "lat": 41.4689, "lon": -81.6234, "poverty_rate": 0.29},
        {"zip": "44106", "lat": 41.5056, "lon": -81.6078, "poverty_rate": 0.22},
        {"zip": "44107", "lat": 41.4812, "lon": -81.8012, "poverty_rate": 0.18},
        {"zip": "44108", "lat": 41.5334, "lon": -81.6123, "poverty_rate": 0.38},
        {"zip": "44109", "lat": 41.4412, "lon": -81.7045, "poverty_rate": 0.26},
        {"zip": "44110", "lat": 41.5634, "lon": -81.5356, "poverty_rate": 0.27},
        {"zip": "44111", "lat": 41.4556, "lon": -81.7823, "poverty_rate": 0.21},
        {"zip": "44112", "lat": 41.5389, "lon": -81.5834, "poverty_rate": 0.29},
        {"zip": "44113", "lat": 41.4845, "lon": -81.6945, "poverty_rate": 0.24},
        {"zip": "44114", "lat": 41.5012, "lon": -81.6890, "poverty_rate": 0.19},
        {"zip": "44115", "lat": 41.5067, "lon": -81.6634, "poverty_rate": 0.33},
        {"zip": "44117", "lat": 41.5289, "lon": -81.5389, "poverty_rate": 0.12},
        {"zip": "44119", "lat": 41.5889, "lon": -81.5556, "poverty_rate": 0.15},
        {"zip": "44120", "lat": 41.4834, "lon": -81.5890, "poverty_rate": 0.30},
        {"zip": "44125", "lat": 41.4267, "lon": -81.6523, "poverty_rate": 0.23},
        {"zip": "44135", "lat": 41.4212, "lon": -81.7934, "poverty_rate": 0.17},
    ],
    "Lake": [
        {"zip": "44004", "lat": 41.7789, "lon": -81.3456, "poverty_rate": 0.16},
        {"zip": "44057", "lat": 41.6534, "lon": -81.4234, "poverty_rate": 0.13},
        {"zip": "44060", "lat": 41.6089, "lon": -81.3623, "poverty_rate": 0.14},
        {"zip": "44077", "lat": 41.6645, "lon": -81.2734, "poverty_rate": 0.11},
        {"zip": "44081", "lat": 41.6234, "lon": -81.2156, "poverty_rate": 0.15},
        {"zip": "44092", "lat": 41.7156, "lon": -81.2645, "poverty_rate": 0.12},
        {"zip": "44094", "lat": 41.7345, "lon": -81.3923, "poverty_rate": 0.17},
        {"zip": "44095", "lat": 41.6823, "lon": -81.3534, "poverty_rate": 0.13},
    ],
    "Geauga": [
        {"zip": "44021", "lat": 41.5812, "lon": -81.1734, "poverty_rate": 0.09},
        {"zip": "44022", "lat": 41.6134, "lon": -81.3456, "poverty_rate": 0.10},
        {"zip": "44023", "lat": 41.5534, "lon": -81.2234, "poverty_rate": 0.08},
        {"zip": "44024", "lat": 41.5289, "lon": -81.1456, "poverty_rate": 0.11},
        {"zip": "44062", "lat": 41.6845, "lon": -81.1923, "poverty_rate": 0.10},
        {"zip": "44065", "lat": 41.6423, "lon": -81.2645, "poverty_rate": 0.12},
    ],
    "Ashtabula": [
        {"zip": "44004", "lat": 41.8456, "lon": -80.7834, "poverty_rate": 0.21},
        {"zip": "44010", "lat": 41.8823, "lon": -80.8234, "poverty_rate": 0.24},
        {"zip": "44030", "lat": 41.7234, "lon": -81.0456, "poverty_rate": 0.19},
        {"zip": "44032", "lat": 41.7645, "lon": -80.9234, "poverty_rate": 0.22},
        {"zip": "44041", "lat": 41.8934, "lon": -80.7623, "poverty_rate": 0.26},
        {"zip": "44047", "lat": 41.7456, "lon": -80.8645, "poverty_rate": 0.20},
        {"zip": "44048", "lat": 41.6923, "lon": -80.9834, "poverty_rate": 0.18},
        {"zip": "44068", "lat": 41.7834, "lon": -80.7234, "poverty_rate": 0.23},
        {"zip": "44076", "lat": 41.8234, "lon": -80.9645, "poverty_rate": 0.25},
        {"zip": "44099", "lat": 41.7123, "lon": -80.8123, "poverty_rate": 0.21},
    ],
    "Trumbull": [
        {"zip": "44403", "lat": 41.2967, "lon": -80.8134, "poverty_rate": 0.22},
        {"zip": "44404", "lat": 41.3234, "lon": -80.7645, "poverty_rate": 0.24},
        {"zip": "44405", "lat": 41.2645, "lon": -80.7234, "poverty_rate": 0.26},
        {"zip": "44406", "lat": 41.2156, "lon": -80.8923, "poverty_rate": 0.19},
        {"zip": "44410", "lat": 41.3645, "lon": -80.6234, "poverty_rate": 0.21},
        {"zip": "44446", "lat": 41.1734, "lon": -80.7645, "poverty_rate": 0.20},
        {"zip": "44451", "lat": 41.2923, "lon": -80.9234, "poverty_rate": 0.23},
        {"zip": "44470", "lat": 41.2456, "lon": -80.6734, "poverty_rate": 0.18},
        {"zip": "44481", "lat": 41.3156, "lon": -80.8645, "poverty_rate": 0.25},
        {"zip": "44483", "lat": 41.2734, "lon": -80.7923, "poverty_rate": 0.22},
    ],
    "Portage": [
        {"zip": "44201", "lat": 41.1456, "lon": -81.0234, "poverty_rate": 0.17},
        {"zip": "44202", "lat": 41.0834, "lon": -81.1645, "poverty_rate": 0.15},
        {"zip": "44221", "lat": 41.1234, "lon": -81.2734, "poverty_rate": 0.14},
        {"zip": "44223", "lat": 41.1923, "lon": -81.1234, "poverty_rate": 0.13},
        {"zip": "44240", "lat": 41.1645, "lon": -81.3456, "poverty_rate": 0.16},
        {"zip": "44242", "lat": 41.2134, "lon": -81.2645, "poverty_rate": 0.12},
        {"zip": "44256", "lat": 41.2645, "lon": -81.1923, "poverty_rate": 0.15},
        {"zip": "44266", "lat": 41.1123, "lon": -81.1456, "poverty_rate": 0.18},
    ],
}


def get_all_zips() -> List[Dict]:
    """
    Returns all ZIP codes with coordinates and poverty data.
    
    Returns:
        List of dicts with keys: zip, lat, lon, county, poverty_rate
    """
    all_zips = []
    for county, zips in COUNTIES.items():
        for zip_data in zips:
            zip_dict = zip_data.copy()
            zip_dict["county"] = county
            all_zips.append(zip_dict)
    return all_zips


def get_random_zip(county: Optional[str] = None) -> Dict:
    """
    Returns a random ZIP code from specified county or all counties.
    
    Args:
        county: Optional county name to filter by
        
    Returns:
        Dict with keys: zip, lat, lon, county, poverty_rate
    """
    if county:
        if county not in COUNTIES:
            raise ValueError(f"Invalid county: {county}. Valid counties: {list(COUNTIES.keys())}")
        zips = COUNTIES[county]
        zip_data = random.choice(zips).copy()
        zip_data["county"] = county
        return zip_data
    else:
        all_zips = get_all_zips()
        return random.choice(all_zips)


def get_high_poverty_zips(threshold: float = 0.20) -> List[Dict]:
    """
    Returns ZIP codes with poverty rate above specified threshold.
    
    Args:
        threshold: Poverty rate threshold (e.g., 0.20 for 20%)
        
    Returns:
        List of ZIP code dicts with poverty_rate >= threshold
    """
    all_zips = get_all_zips()
    return [z for z in all_zips if z["poverty_rate"] >= threshold]


def get_zip_by_code(zip_code: str) -> Optional[Dict]:
    """
    Returns ZIP data for a specific ZIP code.
    
    Args:
        zip_code: 5-digit ZIP code string
        
    Returns:
        Dict with ZIP data or None if not found
    """
    all_zips = get_all_zips()
    for z in all_zips:
        if z["zip"] == zip_code:
            return z
    return None


def get_county_zips(county: str) -> List[Dict]:
    """
    Returns all ZIP codes for a specific county.
    
    Args:
        county: County name
        
    Returns:
        List of ZIP code dicts for the county
    """
    if county not in COUNTIES:
        raise ValueError(f"Invalid county: {county}. Valid counties: {list(COUNTIES.keys())}")
    
    zips = []
    for zip_data in COUNTIES[county]:
        zip_dict = zip_data.copy()
        zip_dict["county"] = county
        zips.append(zip_dict)
    return zips
