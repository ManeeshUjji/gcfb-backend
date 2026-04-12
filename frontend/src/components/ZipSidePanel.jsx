import React, { useState, useEffect } from 'react';
import { forecastAPI } from '../utils/api';
import { useAppContext } from '../context/AppContext';

const ZipSidePanel = ({ zipCode, onClose }) => {
  const { selectedDate } = useAppContext();
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchForecastDetail = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await forecastAPI.getForecastDetail(zipCode, selectedDate);
        setForecastData(response.data);
      } catch (err) {
        console.error('Error fetching forecast detail:', err);
        setError('Failed to load forecast details');
      } finally {
        setLoading(false);
      }
    };

    if (zipCode) {
      fetchForecastDetail();
    }
  }, [zipCode, selectedDate]);

  if (!zipCode) return null;

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl overflow-y-auto z-40">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">ZIP {zipCode}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            &times;
          </button>
        </div>

        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading forecast...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg">
            {error}
          </div>
        )}

        {forecastData && !loading && (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Predicted Headcount
              </h3>
              <p className="text-3xl font-bold text-blue-600">
                {forecastData.predicted_headcount}
              </p>
              {forecastData.confidence_interval && (
                <p className="text-sm text-gray-600 mt-1">
                  Range: {forecastData.confidence_interval.lower} - {forecastData.confidence_interval.upper}
                </p>
              )}
            </div>

            {forecastData.percent_change_vs_last_week !== null && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">
                  Change vs Last Week
                </h3>
                <p className={`text-2xl font-bold ${
                  forecastData.percent_change_vs_last_week > 0 ? 'text-red-600' : 'text-green-600'
                }`}>
                  {forecastData.percent_change_vs_last_week > 0 ? '+' : ''}
                  {forecastData.percent_change_vs_last_week.toFixed(1)}%
                </p>
              </div>
            )}

            {forecastData.top_factors && forecastData.top_factors.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Top Contributing Factors
                </h3>
                <div className="space-y-2">
                  {forecastData.top_factors.map((factor, index) => (
                    <div key={index} className="bg-gray-50 p-3 rounded">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-medium text-gray-700">
                          {factor.feature}
                        </span>
                        <span className="text-sm text-gray-600">
                          {(factor.importance * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{factor.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {forecastData.partner_sites && forecastData.partner_sites.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Partner Sites ({forecastData.partner_sites.length})
                </h3>
                <div className="space-y-3">
                  {forecastData.partner_sites.map((site) => (
                    <div key={site.id} className="border border-gray-200 p-3 rounded-lg">
                      <h4 className="font-medium text-gray-900">{site.name}</h4>
                      <p className="text-sm text-gray-600 mt-1">{site.address}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          {site.program_type}
                        </span>
                        <span className="text-xs text-gray-600">
                          Capacity: {site.capacity_per_day}/day
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        Operating: {site.operating_days}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ZipSidePanel;
