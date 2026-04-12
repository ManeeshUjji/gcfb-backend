import React, { useState, useEffect } from 'react';
import { dispatchAPI, inventoryAPI } from '../utils/api';
import { useAppContext } from '../context/AppContext';
import Map from './Map';

const DispatchPlanner = () => {
  const {
    truckCount,
    setTruckCount,
    volunteerCount,
    setVolunteerCount,
    activeDispatchPlan,
    setActiveDispatchPlan,
    assignments,
  } = useAppContext();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [inventorySummary, setInventorySummary] = useState(null);

  useEffect(() => {
    const loadInventorySummary = async () => {
      try {
        const response = await inventoryAPI.getExpiringItems();
        setInventorySummary({
          total: response.data.total_count,
          urgent: response.data.items.filter((item) => item.urgency === 'red').length,
        });
      } catch (err) {
        console.error('Error loading inventory:', err);
      }
    };

    loadInventorySummary();
  }, []);

  const handleGeneratePlan = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await dispatchAPI.generatePlan({
        truck_count: truckCount,
        volunteer_count: volunteerCount,
        date: null,
      });
      
      setActiveDispatchPlan(response.data);
    } catch (err) {
      console.error('Error generating plan:', err);
      setError('Failed to generate dispatch plan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="flex h-full">
      <div className="w-1/3 bg-white p-6 overflow-y-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Dispatch Planner</h2>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Trucks
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={truckCount}
              onChange={(e) => setTruckCount(parseInt(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Available Volunteers
            </label>
            <input
              type="number"
              min="0"
              value={volunteerCount}
              onChange={(e) => setVolunteerCount(parseInt(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {inventorySummary && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                Warehouse Inventory
              </h3>
              <div className="space-y-1">
                <p className="text-sm text-gray-600">
                  Total expiring items: <strong>{inventorySummary.total}</strong>
                </p>
                <p className="text-sm text-red-600">
                  Urgent (24hrs): <strong>{inventorySummary.urgent}</strong>
                </p>
              </div>
            </div>
          )}

          {assignments.length > 0 && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">
                Expiration Assignments ({assignments.length})
              </h3>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {assignments.map((assignment, index) => (
                  <div key={index} className="text-xs text-blue-800">
                    {assignment.item_name} → {assignment.site_name}
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={handleGeneratePlan}
            disabled={loading || truckCount < 1}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Generating...' : "Generate Today's Plan"}
          </button>

          {error && (
            <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}
        </div>

        {activeDispatchPlan && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Plan Summary</h3>
              <button
                onClick={handlePrint}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Print
              </button>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-sm text-gray-600">
                  Sites served: <strong>{activeDispatchPlan.total_sites_served}</strong>
                </p>
                <p className="text-sm text-gray-600">
                  Total distance: <strong>{activeDispatchPlan.total_distance_miles} mi</strong>
                </p>
                <p className="text-sm text-gray-600">
                  Headcount covered: <strong>{activeDispatchPlan.total_headcount_covered}</strong>
                </p>
              </div>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {activeDispatchPlan.truck_routes.map((route, index) => (
                  <div key={index} className="border border-gray-200 p-3 rounded">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      {route.truck_number}
                    </h4>
                    <p className="text-xs text-gray-600 mb-2">
                      {route.total_distance_miles} mi | {route.estimated_time_hours} hrs | {route.total_load_lbs} lbs
                    </p>
                    <div className="space-y-1">
                      {route.stops.map((stop, stopIndex) => (
                        <div key={stopIndex} className="text-xs text-gray-700">
                          {stop.stop_order}. {stop.site_name} ({stop.quantity_lbs} lbs)
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="w-2/3 bg-gray-100">
        {activeDispatchPlan ? (
          <Map showRoutes={true} />
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                />
              </svg>
              <p className="mt-2">Generate a plan to see routes</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DispatchPlanner;
