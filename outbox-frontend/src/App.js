import React from 'react';
import './App.css'; // Import the custom CSS file
import FileUpload from './components/FileUpload';
import NavigationBar from './components/NavigationBar';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GetProvidersPage from './components/GetProvidersPage';
import ChatPage from './components/ChatPage';

function App() {
  return (
    <Router>
      {/* Main container for the entire application */}
      <div className="app-container">
        {/* Navigation Bar at the very top */}
        <NavigationBar />

        {/* Main content area */}
        <main className="main-content">
          {/* Header for the main content section */}
          <h1 className="app-header-title">
            Outbox Health Assessment
          </h1>

          {/* Routes for different pages */}
          <Routes>
            <Route path="/get-providers" element={<GetProvidersPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/" element={
              <div className="home-upload-section">
                <FileUpload endpoint="/upload-hospital-data" label="Upload Hospital Data" />
                <FileUpload endpoint="/upload-hospital-rating" label="Upload Hospital Rating" />
              </div>
            } />
          </Routes>
        </main>

        {/* Optional: Footer can go here */}
        {/* <footer className="footer">
          <p>&copy; 2023 Outbox Health. All rights reserved.</p>
        </footer> */}
      </div>
    </Router>
  );
}

export default App;
