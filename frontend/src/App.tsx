import React, { useEffect, useState } from 'react';
import { gameApi } from './services/api';
import ResultsTable from './components/ResultsTable';

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Checking...');

  useEffect(() => {
    // Test API connection
    const checkAPI = async () => {
      try {
        const response = await gameApi.healthCheck();
        setApiStatus(`Connected: ${response.status}`);
      } catch (error) {
        setApiStatus('API connection failed');
      }
    };
    
    checkAPI();
  }, []);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif' }}>
      <header style={{ 
        padding: '20px', 
        backgroundColor: '#f8f9fa', 
        borderBottom: '1px solid #dee2e6' 
      }}>
        <h1>NumWatch - Number Result Tracker</h1>
        <p style={{ margin: '5px 0', color: '#666' }}>API Status: {apiStatus}</p>
      </header>
      
      <main>
        <ResultsTable />
      </main>
    </div>
  );
}

export default App;