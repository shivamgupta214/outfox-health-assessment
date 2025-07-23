import React, { useState } from 'react';
import axios from 'axios';

const GetProvidersPage = () => {
  const [zipCode, setZipCode] = useState('');
  const [radius, setRadius] = useState('');
  const [msDrg, setMsDrg] = useState('');
  const [providers, setProviders] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setProviders([]); // Clear previous results

    if (!zipCode || !radius || !msDrg) {
      setError('Please fill in all search fields.');
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.get('http://localhost:8000/providers', {
        params: {
          zip_code: zipCode,
          radius_km: parseFloat(radius), // Ensure radius is a number
          ms_drg: msDrg,
        },
      });
      // Assuming response.data.data contains the array of providers
      if (response.data && response.data.data) {
        setProviders(response.data.data);
        if (response.data.data.length === 0) {
          setError('No providers found matching your criteria.');
        }
      } else {
        setError('Unexpected response format from server.');
      }
    } catch (err) {
      console.error('Error fetching providers:', err);
      setError(`Error fetching providers: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="providers-container">
      <h2>Find Healthcare Providers</h2>
      <form onSubmit={handleSubmit} className="providers-form">
        <div className="form-group">
          <label htmlFor="zipCode" className="form-label">ZIP Code:</label>
          <input
            type="text"
            id="zipCode"
            value={zipCode}
            onChange={(e) => setZipCode(e.target.value)}
            placeholder="e.g., 36301"
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label htmlFor="radius" className="form-label">Radius (km):</label>
          <input
            type="number" // Changed to number type for better input validation
            id="radius"
            value={radius}
            onChange={(e) => setRadius(e.target.value)}
            placeholder="e.g., 25"
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label htmlFor="msDrg" className="form-label">MS DRG Keyword:</label>
          <input
            type="text"
            id="msDrg"
            value={msDrg}
            onChange={(e) => setMsDrg(e.target.value)}
            placeholder="e.g., CHEST PAIN"
            className="form-input"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="search-button"
        >
          {isLoading ? 'Searching...' : 'Search Providers'}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

      <div className="results-section">
        <h3>Search Results:</h3>
        {providers.length > 0 ? (
          <ul className="provider-list">
            {providers.map((provider) => (
              <li key={provider.provider_id} className="provider-card">
                <p className="provider-name">{provider.provider_name}</p>
                <p className="provider-detail">{provider.ms_drg_defination}</p>
                <p className="provider-location">Location: {provider.provider_city}, {provider.provider_state} {provider.provider_zip}</p>
                <p>Avg. Covered Charges: <span className="provider-value">${provider.average_covered_charges?.toFixed(2) || 'N/A'}</span></p>
                <p>Avg. Total Payments: <span className="provider-value">${provider.average_total_payments?.toFixed(2) || 'N/A'}</span></p>
                <p>Star Rating: <span className="provider-value">{provider.star_rating || 'N/A'}/10</span></p>
                <p>Total Discharges: <span className="provider-value">{provider.total_discharges || 'N/A'}</span></p>
              </li>
            ))}
          </ul>
        ) : (
          !isLoading && !error && <p className="no-results-message">No results to display. Use the form above to search.</p>
        )}
      </div>
    </div>
  );
};

export default GetProvidersPage;
