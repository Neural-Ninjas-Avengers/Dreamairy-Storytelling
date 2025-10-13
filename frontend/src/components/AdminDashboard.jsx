import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';

const AdminDashboard = ({ onNavigateToApp }) => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [awsCredentials, setAwsCredentials] = useState({
    accessKeyId: '',
    secretAccessKey: '',
    region: 'eu-west-1'
  });
  const [testResults, setTestResults] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    loadConfiguration();
    loadSystemStatus();
  }, []);

  const loadConfiguration = async () => {
    try {
      console.log('Loading configuration...');
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout
      
      const response = await fetch('/api/v1/admin/config', {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Configuration loaded:', data);
      
      if (data.success) {
        setConfig(data.config);
        
        // Pre-fill AWS credentials if available
        if (data.config.aws?.credentials) {
          setAwsCredentials({
            accessKeyId: data.config.aws.credentials.accessKeyId || '',
            secretAccessKey: '', // Never pre-fill secret
            region: data.config.aws.credentials.region || 'eu-west-1'
          });
        }
      } else {
        console.error('Configuration load failed:', data);
      }
    } catch (error) {
      console.error('Failed to load configuration:', error);
      
      if (error.name === 'AbortError') {
        console.error('Configuration load timed out');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadSystemStatus = async () => {
    try {
      const response = await fetch('/api/v1/admin/monitoring/status');
      const data = await response.json();
      
      if (data.success) {
        setSystemStatus(data.status);
      }
    } catch (error) {
      console.error('Failed to load system status:', error);
    }
  };

  const handleAwsCredentialsSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/v1/admin/config/aws', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(awsCredentials),
      });

      const data = await response.json();

      if (data.success) {
        alert('AWS credentials updated successfully!');
        loadConfiguration();
      } else {
        alert(`Error: ${data.error || data.message}`);
      }
    } catch (error) {
      alert(`Failed to update AWS credentials: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleEnvironmentChange = async (newEnvironment) => {
    if (window.confirm(`Are you sure you want to switch to ${newEnvironment.toUpperCase()} mode?`)) {
      setLoading(true);
      
      // Create a timeout to prevent hanging
      const timeoutId = setTimeout(() => {
        setLoading(false);
        alert('Environment switch timed out. Please try again.');
      }, 15000); // 15 second timeout

      try {
        console.log(`Switching to ${newEnvironment} environment...`);
        
        const controller = new AbortController();
        const timeoutSignal = setTimeout(() => controller.abort(), 10000); // 10 second request timeout
        
        const response = await fetch('/api/v1/admin/config/environment', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ environment: newEnvironment }),
          signal: controller.signal
        });

        clearTimeout(timeoutSignal);
        clearTimeout(timeoutId);

        console.log(`Environment switch response:`, response.status);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log(`Environment switch data:`, data);

        if (data.success) {
          alert(`Successfully switched to ${newEnvironment.toUpperCase()} mode!`);
          await loadConfiguration(); // Reload config after successful switch
        } else {
          alert(`Error switching environment: ${data.error || data.message}`);
        }
      } catch (error) {
        clearTimeout(timeoutId);
        console.error('Environment switch error:', error);
        
        if (error.name === 'AbortError') {
          alert('Environment switch request timed out. Please check your connection and try again.');
        } else {
          alert(`Failed to switch environment: ${error.message}`);
        }
      } finally {
        setLoading(false);
      }
    }
  };

  const handleTestAWSServices = async () => {
    setLoading(true);
    setTestResults(null);

    try {
      const response = await fetch('/api/v1/admin/test/aws', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          services: ['bedrock', 'polly', 'rekognition', 's3', 'dynamodb']
        }),
      });

      const data = await response.json();
      setTestResults(data);

      if (data.success) {
        alert(`AWS Services Test Complete! Overall Status: ${data.overall_status.toUpperCase()}`);
      } else {
        alert(`AWS Services Test Failed: ${data.error}`);
      }
    } catch (error) {
      alert(`Failed to test AWS services: ${error.message}`);
      setTestResults({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleTestStoryGeneration = async () => {
    setLoading(true);
    setTestResults(null);

    try {
      // Create a test session
      const sessionResponse = await fetch('/api/v1/demo/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: 7,
          preferences: ['fantasy'],
          emotional_goal: 'entertain',
          anonymous_id: 'admin_test_user'
        }),
      });

      const sessionData = await sessionResponse.json();

      if (sessionData.session_id) {
        // Generate a test story
        const storyResponse = await fetch(`/api/v1/demo/sessions/${sessionData.session_id}/story`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            theme: 'fantasy',
            segments_so_far: 0,
            child_age: 7,
            emotional_goal: 'entertain'
          }),
        });

        const storyData = await storyResponse.json();
        setTestResults({
          success: true,
          session_id: sessionData.session_id,
          story: storyData
        });

        alert('Story Generation Test Complete! Check results below.');
      } else {
        throw new Error('Failed to create test session');
      }
    } catch (error) {
      alert(`Failed to test story generation: ${error.message}`);
      setTestResults({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  if (loading && !config) {
    return (
      <div className="admin-dashboard loading">
        <div className="loading-spinner">Loading Admin Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <div className="header-left">
          <h1>🛠️ DreamAIry Admin Dashboard</h1>
        </div>
        <div className="header-right">
          <div className="environment-badge">
            Environment: <span className={`env-${config?.environment}`}>{config?.environment?.toUpperCase()}</span>
          </div>
          {onNavigateToApp && (
            <button onClick={onNavigateToApp} className="back-to-app-btn">
              ← Back to App
            </button>
          )}
        </div>
      </header>

      <nav className="admin-nav">
        <button 
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={activeTab === 'aws-config' ? 'active' : ''}
          onClick={() => setActiveTab('aws-config')}
        >
          ☁️ AWS Config
        </button>
        <button 
          className={activeTab === 'environment' ? 'active' : ''}
          onClick={() => setActiveTab('environment')}
        >
          🌍 Environment
        </button>
        <button 
          className={activeTab === 'testing' ? 'active' : ''}
          onClick={() => setActiveTab('testing')}
        >
          🧪 Testing
        </button>
        <button 
          className={activeTab === 'monitoring' ? 'active' : ''}
          onClick={() => setActiveTab('monitoring')}
        >
          📈 Monitoring
        </button>
      </nav>

      <main className="admin-content">
        {activeTab === 'overview' && (
          <div className="tab-content">
            <h2>System Overview</h2>
            
            <div className="overview-grid">
              <div className="overview-card">
                <h3>Current Environment</h3>
                <div className={`environment-status env-${config?.environment}`}>
                  {config?.environment?.toUpperCase() || 'UNKNOWN'}
                </div>
                <p>
                  {config?.environment === 'demo' && 'Using free services and local storage'}
                  {config?.environment === 'staging' && 'Using AWS services with reduced capacity'}
                  {config?.environment === 'production' && 'Using full AWS services'}
                </p>
              </div>

              <div className="overview-card">
                <h3>AWS Status</h3>
                <div className={`aws-status ${config?.aws?.enabled ? 'enabled' : 'disabled'}`}>
                  {config?.aws?.enabled ? '✅ ENABLED' : '❌ DISABLED'}
                </div>
                <p>
                  {config?.aws?.enabled 
                    ? `Connected to ${config?.aws?.region || 'us-east-1'}` 
                    : 'AWS services not configured'
                  }
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'aws-config' && (
          <div className="tab-content">
            <h2>AWS Configuration</h2>
            
            <form onSubmit={handleAwsCredentialsSubmit} className="aws-config-form">
              <div className="form-group">
                <label htmlFor="accessKeyId">AWS Access Key ID:</label>
                <input
                  type="text"
                  id="accessKeyId"
                  value={awsCredentials.accessKeyId}
                  onChange={(e) => setAwsCredentials({
                    ...awsCredentials,
                    accessKeyId: e.target.value
                  })}
                  placeholder="AKIA..."
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="secretAccessKey">AWS Secret Access Key:</label>
                <input
                  type="password"
                  id="secretAccessKey"
                  value={awsCredentials.secretAccessKey}
                  onChange={(e) => setAwsCredentials({
                    ...awsCredentials,
                    secretAccessKey: e.target.value
                  })}
                  placeholder="Enter your secret access key"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="region">AWS Region:</label>
                <select
                  id="region"
                  value={awsCredentials.region}
                  onChange={(e) => setAwsCredentials({
                    ...awsCredentials,
                    region: e.target.value
                  })}
                >
                  <option value="eu-west-1">Europe (Ireland)</option>
                  <option value="us-east-1">US East (N. Virginia)</option>
                  <option value="us-west-2">US West (Oregon)</option>
                  <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                </select>
              </div>

              <button type="submit" disabled={loading} className="submit-btn">
                {loading ? 'Updating...' : 'Update AWS Credentials'}
              </button>
            </form>
          </div>
        )}

        {activeTab === 'environment' && (
          <div className="tab-content">
            <h2>Environment Management</h2>
            
            <div className="environment-section">
              <div className="current-environment">
                <h3>Current Environment</h3>
                <div className={`environment-status env-${config?.environment}`}>
                  {config?.environment?.toUpperCase() || 'UNKNOWN'}
                </div>
              </div>

              <div className="environment-options">
                <h3>Switch Environment</h3>
                <div className="environment-cards">
                  <div className={`env-card ${config?.environment === 'demo' ? 'active' : ''}`}>
                    <h4>🧪 Demo Mode</h4>
                    <p>Free services, local storage, no AWS costs</p>
                    <ul>
                      <li>✅ Local story generation</li>
                      <li>✅ SVG image fallbacks</li>
                      <li>✅ No AWS charges</li>
                      <li>❌ Limited AI capabilities</li>
                    </ul>
                    <button 
                      onClick={() => handleEnvironmentChange('demo')}
                      disabled={loading || config?.environment === 'demo'}
                      className="env-switch-btn demo"
                    >
                      {config?.environment === 'demo' ? 'Current' : 'Switch to Demo'}
                    </button>
                  </div>

                  <div className={`env-card ${config?.environment === 'staging' ? 'active' : ''}`}>
                    <h4>🔧 Staging Mode</h4>
                    <p>AWS services with reduced capacity</p>
                    <ul>
                      <li>✅ AWS AI services</li>
                      <li>✅ Real image generation</li>
                      <li>⚠️ Limited usage</li>
                      <li>💰 Minimal AWS costs</li>
                    </ul>
                    <button 
                      onClick={() => handleEnvironmentChange('staging')}
                      disabled={loading || config?.environment === 'staging'}
                      className="env-switch-btn staging"
                    >
                      {config?.environment === 'staging' ? 'Current' : 'Switch to Staging'}
                    </button>
                  </div>

                  <div className={`env-card ${config?.environment === 'production' ? 'active' : ''}`}>
                    <h4>🚀 Production Mode</h4>
                    <p>Full AWS services and capabilities</p>
                    <ul>
                      <li>✅ Full AWS AI services</li>
                      <li>✅ High-quality generation</li>
                      <li>✅ Unlimited usage</li>
                      <li>💰 Full AWS costs</li>
                    </ul>
                    <button 
                      onClick={() => handleEnvironmentChange('production')}
                      disabled={loading || config?.environment === 'production'}
                      className="env-switch-btn production"
                    >
                      {config?.environment === 'production' ? 'Current' : 'Switch to Production'}
                    </button>
                  </div>
                </div>
              </div>

              <div className="environment-warning">
                <h3>⚠️ Important Notes</h3>
                <ul>
                  <li><strong>Demo Mode:</strong> Perfect for testing without AWS costs</li>
                  <li><strong>Staging Mode:</strong> Use for development with real AWS services</li>
                  <li><strong>Production Mode:</strong> Full capabilities, monitor AWS usage</li>
                  <li><strong>AWS Credentials:</strong> Required for Staging and Production modes</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'testing' && (
          <div className="tab-content">
            <h2>System Testing</h2>
            
            <div className="testing-section">
              <div className="test-controls">
                <button 
                  onClick={handleTestAWSServices}
                  disabled={loading}
                  className="test-btn aws-test"
                >
                  {loading ? 'Testing...' : '🧪 Test AWS Services'}
                </button>
                
                <button 
                  onClick={handleTestStoryGeneration}
                  disabled={loading}
                  className="test-btn story-test"
                >
                  {loading ? 'Testing...' : '📚 Test Story Generation'}
                </button>
              </div>

              {testResults && (
                <div className="test-results">
                  <h3>Test Results</h3>
                  <pre>{JSON.stringify(testResults, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div className="tab-content">
            <h2>System Monitoring</h2>
            
            <div className="monitoring-section">
              <div className="status-grid">
                {systemStatus && Object.entries(systemStatus).map(([service, status]) => (
                  <div key={service} className={`status-card ${status.status}`}>
                    <h4>{service.toUpperCase()}</h4>
                    <div className={`status-indicator ${status.status}`}>
                      {status.status === 'healthy' ? '✅' : '❌'} {status.status.toUpperCase()}
                    </div>
                    {status.response_time && (
                      <p>Response Time: {status.response_time}ms</p>
                    )}
                    {status.error && (
                      <p className="error-message">Error: {status.error}</p>
                    )}
                  </div>
                ))}
              </div>
              
              <button 
                onClick={loadSystemStatus}
                disabled={loading}
                className="refresh-btn"
              >
                {loading ? 'Refreshing...' : '🔄 Refresh Status'}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboard;