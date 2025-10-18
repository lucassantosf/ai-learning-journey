import React, { useState, useEffect } from 'react';
import { healthCheck } from '../services/api';

const HealthCheck: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthy = await healthCheck();
        setIsHealthy(healthy);
        setErrorMessage(healthy ? '' : 'Backend is not responding');
      } catch (error) {
        setIsHealthy(false);
        setErrorMessage('Health check failed');
        console.error('Health check error:', error);
      }
    };

    // Initial check
    checkHealth();

    // Check every 30 seconds
    const intervalId = setInterval(checkHealth, 30000);

    // Cleanup interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  const getBadgeStyle = () => {
    if (isHealthy === null) {
      return 'bg-gray-500 text-white border-2 border-gray-600';
    }
    return isHealthy 
      ? 'bg-green-500 text-white border-2 border-green-600 animate-pulse' 
      : 'bg-red-500 text-white border-2 border-red-600 animate-bounce';
  };

  const getStatusText = () => {
    if (isHealthy === null) return 'Checking';
    return isHealthy ? 'API Healthy' : 'API Offline';
  };

  return (
    <div className="self-end w-full">
      <div 
        className={`mb-4 px-4 py-2 rounded-full text-sm font-bold shadow-lg transition-all duration-300 ease-in-out ${getBadgeStyle()}`}
        title={`Backend Status: ${getStatusText()}`}
      >
        {getStatusText()}
      </div>
      {errorMessage && (
        <div className="text-red-500 text-sm text-right mr-4">
          {errorMessage}
        </div>
      )}
    </div>
  );
};

export default HealthCheck;
