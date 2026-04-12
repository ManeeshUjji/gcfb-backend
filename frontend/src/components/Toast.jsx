import React, { useEffect } from 'react';

const Toast = ({ message, type = 'info', onClose, duration = 5000 }) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const typeStyles = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-orange-500',
    info: 'bg-blue-500',
  };

  return (
    <div className={`fixed top-4 right-4 ${typeStyles[type]} text-white px-6 py-4 rounded-lg shadow-lg z-50 max-w-md`}>
      <div className="flex items-center justify-between">
        <span>{message}</span>
        <button
          onClick={onClose}
          className="ml-4 text-white hover:text-gray-200 font-bold text-xl"
        >
          &times;
        </button>
      </div>
    </div>
  );
};

export default Toast;
