import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  const [selectedDate, setSelectedDate] = useState('today');
  const [selectedZip, setSelectedZip] = useState(null);
  const [activeDispatchPlan, setActiveDispatchPlan] = useState(null);
  const [truckCount, setTruckCount] = useState(3);
  const [volunteerCount, setVolunteerCount] = useState(100);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const addAssignment = (assignment) => {
    setAssignments((prev) => [...prev, assignment]);
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    selectedDate,
    setSelectedDate,
    selectedZip,
    setSelectedZip,
    activeDispatchPlan,
    setActiveDispatchPlan,
    truckCount,
    setTruckCount,
    volunteerCount,
    setVolunteerCount,
    assignments,
    addAssignment,
    loading,
    setLoading,
    error,
    setError,
    clearError,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
