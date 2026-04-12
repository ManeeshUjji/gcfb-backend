import React, { useState, useEffect } from 'react';
import { inventoryAPI, dispatchAPI } from '../utils/api';
import { useAppContext } from '../context/AppContext';

const ExpirationFeed = () => {
  const { addAssignment } = useAppContext();
  const [expiringItems, setExpiringItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [suggestedSites, setSuggestedSites] = useState([]);
  const [loadingSites, setLoadingSites] = useState(false);
  const [assigningItemId, setAssigningItemId] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    loadExpiringItems();
  }, []);

  const loadExpiringItems = async () => {
    try {
      setLoading(true);
      const response = await inventoryAPI.getExpiringItems();
      setExpiringItems(response.data.items);
    } catch (err) {
      console.error('Error loading expiring items:', err);
      setError('Failed to load expiring items');
    } finally {
      setLoading(false);
    }
  };

  const handleFindSites = async (itemId) => {
    try {
      setLoadingSites(true);
      setSelectedItem(itemId);
      setSuggestedSites([]);
      
      const response = await inventoryAPI.getSuggestedSites(itemId);
      setSuggestedSites(response.data.suggested_sites);
    } catch (err) {
      console.error('Error finding sites:', err);
      setError('Failed to find suggested sites');
    } finally {
      setLoadingSites(false);
    }
  };

  const handleAssign = async (itemId, siteId) => {
    try {
      setAssigningItemId(`${itemId}-${siteId}`);
      
      const response = await dispatchAPI.assignToDispatch({
        item_id: itemId,
        site_id: siteId,
      });
      
      addAssignment(response.data.assignment);
      
      setSuccessMessage(`Successfully assigned to ${response.data.assignment.site_name}`);
      setTimeout(() => setSuccessMessage(null), 3000);
      
      setSelectedItem(null);
      setSuggestedSites([]);
      
      await loadExpiringItems();
    } catch (err) {
      console.error('Error assigning item:', err);
      setError('Failed to assign item to site');
    } finally {
      setAssigningItemId(null);
    }
  };

  const getUrgencyColor = (urgency) => {
    const colors = {
      red: 'bg-red-100 border-red-400 text-red-800',
      orange: 'bg-orange-100 border-orange-400 text-orange-800',
      yellow: 'bg-yellow-100 border-yellow-400 text-yellow-800',
    };
    return colors[urgency] || 'bg-gray-100 border-gray-400 text-gray-800';
  };

  const getUrgencyLabel = (urgency) => {
    const labels = {
      red: 'URGENT',
      orange: 'High Priority',
      yellow: 'Medium Priority',
    };
    return labels[urgency] || 'Low Priority';
  };

  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-gray-600">Loading expiring items...</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Expiration Alerts</h2>
        <span className="text-sm text-gray-600">{expiringItems.length} items expiring soon</span>
      </div>

      {successMessage && (
        <div className="bg-green-50 text-green-700 p-4 rounded-lg mb-4">
          {successMessage}
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-4">
          {error}
          <button
            onClick={() => setError(null)}
            className="ml-4 text-red-800 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {expiringItems.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
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
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="mt-2 text-gray-600">No items expiring within 72 hours</p>
        </div>
      ) : (
        <div className="space-y-4">
          {expiringItems.map((item) => (
            <div
              key={item.id}
              className={`border-l-4 p-4 rounded-lg ${getUrgencyColor(item.urgency)}`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <h3 className="text-lg font-semibold">{item.item_name}</h3>
                    <span className="ml-3 text-xs font-bold px-2 py-1 rounded">
                      {getUrgencyLabel(item.urgency)}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <p>
                      <span className="font-medium">Quantity:</span> {item.quantity} {item.unit}
                    </p>
                    <p>
                      <span className="font-medium">Category:</span> {item.category}
                    </p>
                    <p>
                      <span className="font-medium">Expires:</span>{' '}
                      {new Date(item.expiration_date).toLocaleDateString()}
                    </p>
                    <p>
                      <span className="font-medium">Days left:</span> {item.days_until_expiration}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => handleFindSites(item.id)}
                  disabled={loadingSites && selectedItem === item.id}
                  className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors text-sm font-medium"
                >
                  {loadingSites && selectedItem === item.id ? 'Finding...' : 'Find Sites'}
                </button>
              </div>

              {selectedItem === item.id && suggestedSites.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-300">
                  <h4 className="font-semibold mb-3">Suggested Partner Sites:</h4>
                  <div className="space-y-2">
                    {suggestedSites.map((site) => (
                      <div
                        key={site.site_id}
                        className="bg-white p-3 rounded border border-gray-300 flex justify-between items-start"
                      >
                        <div className="flex-1">
                          <h5 className="font-medium text-gray-900">{site.site_name}</h5>
                          <p className="text-sm text-gray-600">{site.address}</p>
                          <div className="flex items-center mt-2 space-x-4 text-xs text-gray-600">
                            <span>{site.distance_miles} miles</span>
                            <span>Demand: {site.predicted_demand}</span>
                            <span className="text-blue-600 font-medium">
                              Score: {site.match_score}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{site.explanation}</p>
                        </div>
                        
                        <button
                          onClick={() => handleAssign(item.id, site.site_id)}
                          disabled={assigningItemId === `${item.id}-${site.site_id}`}
                          className="ml-4 bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 disabled:bg-gray-400 transition-colors text-sm"
                        >
                          {assigningItemId === `${item.id}-${site.site_id}` ? 'Assigning...' : 'Assign'}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ExpirationFeed;
