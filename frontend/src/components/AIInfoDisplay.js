import React, { useState, useEffect } from 'react';
import './AIInfoDisplay.css';

const AIInfoDisplay = () => {
  const [aiInfo, setAiInfo] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAIInfo();
  }, []);

  const fetchAIInfo = async () => {
    try {
      const response = await fetch('/api/v1/ai-info/current');
      if (response.ok) {
        const data = await response.json();
        setAiInfo(data);
      }
    } catch (error) {
      console.error('Failed to fetch AI info:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="ai-info-display loading">
        <div className="ai-info-icon">🤖</div>
      </div>
    );
  }

  if (!aiInfo) {
    return null;
  }

  const handleToggleDetails = () => {
    setShowDetails(!showDetails);
  };

  return (
    <div className="ai-info-display">
      <div className="ai-info-icon" onClick={handleToggleDetails} title="Click to see AI details">
        {aiInfo.mode_icon || '🤖'}
      </div>
      
      {showDetails && (
        <div className="ai-info-popup">
          <div className="ai-info-header">
            <h3>{aiInfo.mode_icon} {aiInfo.mode_name}</h3>
            <button className="close-btn" onClick={handleToggleDetails}>×</button>
          </div>
          
          <div className="ai-info-content">
            <div className="environment-info">
              <div className="environment-badge">
                <span className={`env-indicator env-${aiInfo.environment}`}>
                  {aiInfo.environment.toUpperCase()}
                </span>
              </div>
              <div className="cost-info">
                <span className={`cost-badge ${aiInfo.using_aws_services ? 'paid' : 'free'}`}>
                  {aiInfo.cost_warning}
                </span>
              </div>
            </div>

            <div className="services-list">
              <h4>AI Services Active:</h4>
              {Object.entries(aiInfo.services).map(([serviceKey, service]) => (
                <div key={serviceKey} className="service-item">
                  <div className="service-icon">{service.icon}</div>
                  <div className="service-details">
                    <div className="service-name">{service.provider}</div>
                    <div className="service-model">{service.model}</div>
                    <div className="service-description">{service.description}</div>
                  </div>
                  <div className={`service-cost ${service.cost}`}>
                    {service.cost === 'paid' ? '💰' : '🆓'}
                  </div>
                </div>
              ))}
            </div>

            {aiInfo.using_aws_services && (
              <div className="aws-info">
                <div className="aws-region">
                  <strong>AWS Region:</strong> {aiInfo.aws_region}
                </div>
                <div className="quality-indicator">
                  <strong>Quality:</strong> 
                  <span className="quality-badge high">High Quality AI</span>
                </div>
              </div>
            )}

            {!aiInfo.using_aws_services && (
              <div className="free-info">
                <div className="quality-indicator">
                  <strong>Quality:</strong> 
                  <span className="quality-badge basic">Basic Quality</span>
                </div>
                <div className="upgrade-hint">
                  💡 Switch to Staging/Production mode for high-quality AWS AI
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIInfoDisplay;