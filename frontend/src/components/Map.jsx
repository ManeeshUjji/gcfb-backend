import React, { useState, useEffect, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { forecastAPI, sitesAPI } from '../utils/api';
import { useAppContext } from '../context/AppContext';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const Map = ({ onZipClick, showRoutes = false }) => {
  const { selectedDate, activeDispatchPlan } = useAppContext();
  const [geoJsonData, setGeoJsonData] = useState(null);
  const [forecastData, setForecastData] = useState({});
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const geoJsonLayerRef = useRef(null);

  useEffect(() => {
    const loadGeoJson = async () => {
      try {
        const response = await fetch('/ohio_zips.geojson');
        const data = await response.json();
        setGeoJsonData(data);
      } catch (err) {
        console.error('Error loading GeoJSON:', err);
        setError('Failed to load map data');
      }
    };

    loadGeoJson();
  }, []);

  useEffect(() => {
    const loadForecastData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await forecastAPI.getForecast(selectedDate);
        const forecastMap = {};
        response.data.forecasts.forEach((forecast) => {
          forecastMap[forecast.zip_code] = forecast;
        });
        setForecastData(forecastMap);
      } catch (err) {
        console.error('Error loading forecast:', err);
        const errorMessage = err.code === 'ECONNABORTED' 
          ? 'Request timed out. The forecast API is taking longer than expected (this is normal for first load).'
          : err.response?.data?.detail || 'Failed to load forecast data. Please check that the backend is running.';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    loadForecastData();
  }, [selectedDate]);

  useEffect(() => {
    const loadSites = async () => {
      try {
        const response = await sitesAPI.getAllSites();
        setSites(response.data);
      } catch (err) {
        console.error('Error loading sites:', err);
      }
    };

    loadSites();
  }, []);

  const getColor = (colorCode) => {
    const colors = {
      green: '#10b981',
      yellow: '#f59e0b',
      red: '#ef4444',
    };
    return colors[colorCode] || '#9ca3af';
  };

  const style = (feature) => {
    const zipCode = feature.properties.ZCTA5CE10 || feature.properties.GEOID10;
    const forecast = forecastData[zipCode];
    const color = forecast ? getColor(forecast.color_code) : '#e5e7eb';

    return {
      fillColor: color,
      weight: 1,
      opacity: 1,
      color: '#ffffff',
      fillOpacity: 0.6,
    };
  };

  const onEachFeature = (feature, layer) => {
    const zipCode = feature.properties.ZCTA5CE10 || feature.properties.GEOID10;
    const forecast = forecastData[zipCode];

    layer.on({
      mouseover: (e) => {
        const layer = e.target;
        layer.setStyle({
          weight: 3,
          fillOpacity: 0.8,
        });
      },
      mouseout: (e) => {
        if (geoJsonLayerRef.current) {
          geoJsonLayerRef.current.resetStyle(e.target);
        }
      },
      click: () => {
        if (onZipClick && zipCode) {
          onZipClick(zipCode);
        }
      },
    });

    if (forecast) {
      layer.bindTooltip(
        `<strong>ZIP: ${zipCode}</strong><br/>
         Predicted: ${forecast.predicted_headcount}<br/>
         Sites: ${forecast.num_sites}`,
        { sticky: true }
      );
    } else {
      layer.bindTooltip(`<strong>ZIP: ${zipCode}</strong><br/>No forecast data`, {
        sticky: true,
      });
    }
  };

  const routeColors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <p className="text-red-600 font-semibold">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Reload
          </button>
        </div>
      </div>
    );
  }

  if (!geoJsonData) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading map...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative">
      {loading && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg z-[1000] flex items-center space-x-3 max-w-2xl">
          <div className="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white flex-shrink-0"></div>
          <span className="font-medium">Loading forecast data... Generating ML predictions for 60 sites. This typically takes 30-90 seconds on first load.</span>
        </div>
      )}
      
      <MapContainer
        center={[41.5, -81.7]}
        zoom={9}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {geoJsonData && Object.keys(forecastData).length > 0 && (
          <GeoJSON
            key={`geojson-${selectedDate}-${Object.keys(forecastData).length}`}
            ref={geoJsonLayerRef}
            data={geoJsonData}
            style={style}
            onEachFeature={onEachFeature}
          />
        )}

        {sites.map((site) => (
          <Marker
            key={site.id}
            position={[site.latitude, site.longitude]}
          >
            <Popup>
              <div>
                <strong>{site.name}</strong>
                <br />
                {site.address}
                <br />
                <span className="text-sm text-gray-600">{site.program_type}</span>
              </div>
            </Popup>
          </Marker>
        ))}

        {showRoutes && activeDispatchPlan && activeDispatchPlan.truck_routes && (
          <>
            {activeDispatchPlan.truck_routes.map((route, routeIndex) => {
              const warehouseLat = 41.4993;
              const warehouseLon = -81.6944;
              
              const positions = [
                [warehouseLat, warehouseLon],
                ...route.stops.map((stop) => [stop.latitude, stop.longitude]),
                [warehouseLat, warehouseLon],
              ];

              return (
                <Polyline
                  key={routeIndex}
                  positions={positions}
                  color={routeColors[routeIndex % routeColors.length]}
                  weight={3}
                  opacity={0.7}
                />
              );
            })}
          </>
        )}
      </MapContainer>

      <div className="absolute bottom-4 right-4 bg-white p-4 rounded-lg shadow-lg z-[1000]">
        <h4 className="font-semibold text-gray-900 mb-2">Legend</h4>
        <div className="space-y-1">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 mr-2 rounded"></div>
            <span className="text-sm text-gray-700">Low demand (&lt;70%)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-500 mr-2 rounded"></div>
            <span className="text-sm text-gray-700">Medium (70-90%)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 mr-2 rounded"></div>
            <span className="text-sm text-gray-700">High demand (&gt;90%)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Map;
