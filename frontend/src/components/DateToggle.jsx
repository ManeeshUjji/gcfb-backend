import React from 'react';
import { useAppContext } from '../context/AppContext';

const DateToggle = () => {
  const { selectedDate, setSelectedDate } = useAppContext();

  const dateOptions = [
    { value: 'today', label: 'Today' },
    { value: 'tomorrow', label: 'Tomorrow' },
    { value: 'week', label: 'This Week' },
  ];

  return (
    <div className="flex space-x-2 bg-white p-4 rounded-lg shadow">
      {dateOptions.map((option) => (
        <button
          key={option.value}
          onClick={() => setSelectedDate(option.value)}
          className={`px-6 py-2 rounded-lg font-medium transition-colors ${
            selectedDate === option.value
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};

export default DateToggle;
