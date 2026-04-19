import React, { useState, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const HEALTH_URL = API_BASE_URL.replace(/\/api\/?$/, '') + '/health';

const ConnectionStatus = () => {
  const [status, setStatus] = useState('checking');
  const [details, setDetails] = useState('');

  useEffect(() => {
    let isMounted = true;
    
    const checkConnection = async () => {
      try {
        const response = await fetch(HEALTH_URL, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        });
        
        if (!isMounted) return;
        
        if (response.ok) {
          const data = await response.json();
          const { status: healthStatus, database } = data;
          
          if (healthStatus === 'healthy') {
            setStatus('connected');
            setDetails('Backend API is operational');
          } else if (healthStatus === 'degraded') {
            setStatus('degraded');
            setDetails(`Backend degraded - Database: ${database}`);
          } else {
            setStatus('connected');
            setDetails('Backend is responding');
          }
        } else {
          setStatus('degraded');
          setDetails(`Backend returned status ${response.status}`);
        }
      } catch (err) {
        if (!isMounted) return;
        
        console.error('Connection check failed:', err);
        setStatus('disconnected');
        setDetails(err.message || 'Connection error');
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const statusColors = {
    checking: 'bg-gray-500',
    connected: 'bg-green-500',
    degraded: 'bg-yellow-500',
    disconnected: 'bg-red-500',
  };

  const statusText = {
    checking: 'Checking...',
    connected: 'Connected',
    degraded: 'Degraded',
    disconnected: 'Disconnected',
  };

  if (status === 'connected') return null;

  return (
    <div className="fixed bottom-4 right-4 bg-white p-4 rounded-lg shadow-lg border-2 border-gray-200 z-50 max-w-sm">
      <div className="flex items-center space-x-3">
        <div className={`w-3 h-3 rounded-full ${statusColors[status]} animate-pulse`}></div>
        <div>
          <div className="font-semibold text-gray-900">{statusText[status]}</div>
          <div className="text-sm text-gray-600">{details}</div>
        </div>
      </div>
      {status === 'disconnected' && (
        <div className="mt-3 text-xs text-gray-500">
          <p>Make sure the backend is running:</p>
          <code className="block mt-1 bg-gray-100 p-2 rounded">
            cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
          </code>
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus;
