import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = ({ endpoint, label }) => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage(''); // Clear message when a new file is selected
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file to upload.');
      return;
    }

    setIsUploading(true);
    setMessage('Uploading...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const url = "http://127.0.0.1:8000" + endpoint
      console.log(url)
      const response = await axios.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage(response.data.message || 'File uploaded successfully!');
    } catch (error) {
      console.error('Error uploading file:', error);
      setMessage(`Error uploading file: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsUploading(false);
      setFile(null); // Clear file input after upload attempt
    }
  };

  return (
    <div className="file-upload-container">
      <h3>{label}</h3>
      <div className="file-upload-content">
        <input
          type="file"
          onChange={handleFileChange}
          className="file-input"
        />
        <button
          onClick={handleUpload}
          disabled={!file || isUploading}
          className="upload-button"
        >
          {isUploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      {message && (
        <p className={`upload-message ${message.startsWith('Error') ? 'error' : 'success'}`}>
          {message}
        </p>
      )}
    </div>
  );
};

export default FileUpload;
