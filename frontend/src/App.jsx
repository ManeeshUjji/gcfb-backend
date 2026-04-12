import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import ErrorBoundary from './components/ErrorBoundary';
import Toast from './components/Toast';
import ConnectionStatus from './components/ConnectionStatus';
import Map from './components/Map';
import DateToggle from './components/DateToggle';
import ZipSidePanel from './components/ZipSidePanel';
import DispatchPlanner from './components/DispatchPlanner';
import ExpirationFeed from './components/ExpirationFeed';

const HeatmapView = () => {
  const [selectedZip, setSelectedZip] = useState(null);

  return (
    <div className="h-screen flex flex-col">
      <div className="p-4 bg-white shadow-sm">
        <DateToggle />
      </div>
      <div className="flex-1 relative">
        <Map onZipClick={setSelectedZip} />
        {selectedZip && (
          <ZipSidePanel zipCode={selectedZip} onClose={() => setSelectedZip(null)} />
        )}
      </div>
    </div>
  );
};

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Demand Heatmap' },
    { path: '/dispatch', label: 'Dispatch Planner' },
    { path: '/alerts', label: 'Expiration Alerts' },
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex space-x-8">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                location.pathname === item.path
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

function AppContent() {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            GCFB Operational Intelligence Dashboard
          </h1>
        </div>
      </header>

      <Navigation />

      <main className="h-[calc(100vh-180px)]">
        <Routes>
          <Route path="/" element={<HeatmapView />} />
          <Route path="/dispatch" element={<DispatchPlanner />} />
          <Route path="/alerts" element={<ExpirationFeed />} />
        </Routes>
      </main>

      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => removeToast(toast.id)}
        />
      ))}

      <ConnectionStatus />
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AppProvider>
        <Router>
          <AppContent />
        </Router>
      </AppProvider>
    </ErrorBoundary>
  );
}

export default App;
