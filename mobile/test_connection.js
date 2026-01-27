// Simple test to verify mobile app can connect to backend
import axios from 'axios';

async function testConnection() {
  try {
    console.log('Testing connection to backend...');
    
    // Test the health endpoint
    const response = await axios.get('http://localhost:8000/api/health');
    console.log('✅ Health check successful:', response.data.status);
    
    // Test the dashboard endpoint
    const dashboardResponse = await axios.get('http://localhost:8000/api/dashboard');
    console.log('✅ Dashboard data retrieved:', dashboardResponse.data);
    
    // Test getting pending tasks
    const tasksResponse = await axios.get('http://localhost:8000/api/tasks/pending');
    console.log('✅ Pending tasks retrieved:', tasksResponse.data.count, 'tasks');
    
    console.log('\n🎉 All tests passed! Mobile app should be able to connect to the backend.');
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
  }
}

// For testing from Node.js environment
if (typeof window === 'undefined') {
  testConnection();
}