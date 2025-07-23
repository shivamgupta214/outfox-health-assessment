import React from 'react';
import { useNavigate } from 'react-router-dom';

const NavigationBar = () => {
  const navigate = useNavigate();

  const handleNavigate = (path) => {
    navigate(path);
  };

  return (
    <nav className="navbar">
      <button
        onClick={() => handleNavigate('/')}
        className="navbar-button"
      >
        Home
      </button>
      <button
        onClick={() => handleNavigate('/get-providers')}
        className="navbar-button"
      >
        Get Providers
      </button>
      <button
        onClick={() => handleNavigate('/chat')}
        className="navbar-button"
      >
        AI Chat
      </button>
    </nav>
  );
};

export default NavigationBar;
