import json
import os
from typing import Dict, List, Optional
import sys

sys.path.append('..')
from data.zip_coordinates import get_all_zips


_poverty_cache = None


def load_poverty_data() -> Dict[str, float]:
    """
    Load census poverty rate data by ZIP code.
    Uses ZIP coordinate data which includes poverty rates.
    
    Returns:
        Dict mapping ZIP code to poverty rate
    """
    global _poverty_cache
    
    if _poverty_cache is not None:
        return _poverty_cache
    
    zip_data = get_all_zips()
    _poverty_cache = {z['zip']: z['poverty_rate'] for z in zip_data}
    
    return _poverty_cache


def calculate_equity_weight(zip_code: str, poverty_data: Optional[Dict] = None) -> float:
    """
    Calculate equity weight for a ZIP code based on poverty rate.
    Higher poverty = higher priority weight in dispatch optimization.
    
    Args:
        zip_code: ZIP code to calculate weight for
        poverty_data: Optional poverty data dict. If None, loads automatically.
    
    Returns:
        Equity weight multiplier (1.0 to 2.0)
        - 1.0 for low poverty areas (<10%)
        - 1.5 for moderate poverty (10-20%)
        - 2.0 for high poverty (>30%)
    """
    if poverty_data is None:
        poverty_data = load_poverty_data()
    
    poverty_rate = poverty_data.get(zip_code, 0.15)
    
    if poverty_rate < 0.10:
        weight = 1.0
    elif poverty_rate < 0.15:
        weight = 1.2
    elif poverty_rate < 0.20:
        weight = 1.5
    elif poverty_rate < 0.25:
        weight = 1.7
    else:
        weight = 2.0
    
    return weight


def get_high_need_zips(threshold: float = 0.2) -> List[str]:
    """
    Return list of ZIP codes above poverty threshold.
    
    Args:
        threshold: Minimum poverty rate (default 0.2 = 20%)
    
    Returns:
        List of ZIP codes with poverty rate above threshold
    """
    poverty_data = load_poverty_data()
    
    high_need = [
        zip_code
        for zip_code, poverty_rate in poverty_data.items()
        if poverty_rate >= threshold
    ]
    
    return sorted(high_need)


def get_poverty_rate(zip_code: str) -> float:
    """
    Get poverty rate for a specific ZIP code.
    
    Args:
        zip_code: ZIP code to look up
    
    Returns:
        Poverty rate (0.0 to 1.0), or 0.15 (15%) if not found
    """
    poverty_data = load_poverty_data()
    return poverty_data.get(zip_code, 0.15)


def rank_sites_by_equity(sites: List[Dict]) -> List[Dict]:
    """
    Rank sites by equity priority (highest need first).
    
    Args:
        sites: List of site dicts with 'zip_code' key
    
    Returns:
        List of sites sorted by equity weight (descending)
    """
    poverty_data = load_poverty_data()
    
    for site in sites:
        site['equity_weight'] = calculate_equity_weight(site['zip_code'], poverty_data)
        site['poverty_rate'] = poverty_data.get(site['zip_code'], 0.15)
    
    return sorted(sites, key=lambda x: x['equity_weight'], reverse=True)
