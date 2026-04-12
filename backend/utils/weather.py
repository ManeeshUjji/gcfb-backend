import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv


class WeatherService:
    """
    Weather service with caching and error handling.
    Free tier API access with fallback mechanisms.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize weather service.
        
        Args:
            api_key: OpenWeatherMap API key. If None, loads from environment.
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
        
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
    
    def _get_cache_key(self, endpoint: str, lat: float, lon: float) -> str:
        """Generate cache key for request."""
        return f"{endpoint}_{lat}_{lon}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cached data is still valid."""
        if 'timestamp' not in cache_entry:
            return False
        
        age = datetime.now() - cache_entry['timestamp']
        return age < self.cache_duration
    
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch current weather for given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dict with weather data or None if API fails
        """
        cache_key = self._get_cache_key('current', lat, lon)
        
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'imperial'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            weather_data = {
                'temperature_f': data['main']['temp'],
                'feels_like_f': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'precipitation_inches': self._convert_mm_to_inches(
                    data.get('rain', {}).get('1h', 0) + data.get('snow', {}).get('1h', 0)
                )
            }
            
            self.cache[cache_key] = {
                'data': weather_data,
                'timestamp': datetime.now()
            }
            
            return weather_data
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return self.handle_api_failure(e)
    
    def get_forecast(self, lat: float, lon: float, days: int = 7) -> Optional[List[Dict]]:
        """
        Fetch weather forecast for specified number of days.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days to forecast (max 7)
            
        Returns:
            List of daily forecast dictionaries
        """
        cache_key = self._get_cache_key('forecast', lat, lon)
        
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]['data'][:days]
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'imperial',
                'cnt': min(days * 8, 40)
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            daily_forecasts = self._aggregate_to_daily(data['list'])
            
            self.cache[cache_key] = {
                'data': daily_forecasts,
                'timestamp': datetime.now()
            }
            
            return daily_forecasts[:days]
            
        except Exception as e:
            print(f"Forecast API error: {e}")
            return self._get_fallback_forecast(days)
    
    def _aggregate_to_daily(self, forecast_list: List[Dict]) -> List[Dict]:
        """
        Aggregate 3-hour forecasts into daily forecasts.
        
        Args:
            forecast_list: List of 3-hour interval forecasts
            
        Returns:
            List of daily forecast summaries
        """
        daily_data = {}
        
        for item in forecast_list:
            dt = datetime.fromtimestamp(item['dt'])
            date_key = dt.date()
            
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'temps': [],
                    'precip': [],
                    'descriptions': []
                }
            
            daily_data[date_key]['temps'].append(item['main']['temp'])
            daily_data[date_key]['precip'].append(
                self._convert_mm_to_inches(
                    item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
                )
            )
            daily_data[date_key]['descriptions'].append(item['weather'][0]['description'])
        
        daily_forecasts = []
        for date_key in sorted(daily_data.keys()):
            data = daily_data[date_key]
            daily_forecasts.append({
                'date': date_key,
                'temperature_f': sum(data['temps']) / len(data['temps']),
                'temp_min_f': min(data['temps']),
                'temp_max_f': max(data['temps']),
                'precipitation_inches': sum(data['precip']),
                'description': max(set(data['descriptions']), key=data['descriptions'].count)
            })
        
        return daily_forecasts
    
    def _convert_mm_to_inches(self, mm: float) -> float:
        """Convert millimeters to inches."""
        return mm * 0.0393701
    
    def handle_api_failure(self, error: Exception) -> Dict:
        """
        Provide fallback data when API is unavailable.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Dict with default weather values
        """
        print(f"Using fallback weather data due to: {error}")
        
        month = datetime.now().month
        
        if month in [12, 1, 2]:
            temp = 30.0
            precip = 0.15
        elif month in [6, 7, 8]:
            temp = 75.0
            precip = 0.05
        elif month in [3, 4, 5]:
            temp = 55.0
            precip = 0.2
        else:
            temp = 50.0
            precip = 0.1
        
        return {
            'temperature_f': temp,
            'feels_like_f': temp,
            'humidity': 65,
            'description': 'unavailable',
            'precipitation_inches': precip
        }
    
    def _get_fallback_forecast(self, days: int) -> List[Dict]:
        """
        Generate fallback forecast data.
        
        Args:
            days: Number of days to generate
            
        Returns:
            List of daily forecasts with seasonal defaults
        """
        forecasts = []
        
        for i in range(days):
            forecast_date = datetime.now().date() + timedelta(days=i)
            fallback = self.handle_api_failure(Exception("API unavailable"))
            
            forecasts.append({
                'date': forecast_date,
                'temperature_f': fallback['temperature_f'],
                'temp_min_f': fallback['temperature_f'] - 5,
                'temp_max_f': fallback['temperature_f'] + 5,
                'precipitation_inches': fallback['precipitation_inches'],
                'description': 'seasonal average (fallback)'
            })
        
        return forecasts


_weather_service_instance = None


def get_weather_service() -> WeatherService:
    """
    Get singleton instance of WeatherService.
    
    Returns:
        WeatherService instance
    """
    global _weather_service_instance
    
    if _weather_service_instance is None:
        _weather_service_instance = WeatherService()
    
    return _weather_service_instance
