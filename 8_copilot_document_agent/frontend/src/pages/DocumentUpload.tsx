import React, { useState, useRef } from 'react';
import { Link } from 'react-router-dom';

const DocumentUpload: React.FC = () => {
  const [documents, setDocuments] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const newFiles = Array.from(event.target.files);
      setDocuments(prevDocuments => [...prevDocuments, ...newFiles]);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer.files) {
      const droppedFiles = Array.from(event.dataTransfer.files);
      setDocuments(prevDocuments => [...prevDocuments, ...droppedFiles]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const removeDocument = (indexToRemove: number) => {
    setDocuments(prevDocuments => 
      prevDocuments.filter((_, index) => index !== indexToRemove)
    );
  };

  return (
    <div className="document-upload">
      <Link to="/" className="back-button">
        <span className="back-button-icon">←</span>
        Back to Home
      </Link>

      <div className="upload-container">
        <div className="upload-header">
          <h2>Document Upload</h2>
          <p>Upload PDF and DOCX files for intelligent analysis</p>
        </div>

        <input 
          type="file" 
          ref={fileInputRef}
          className="file-upload-input"
          accept=".pdf,.docx"
          multiple 
          onChange={handleFileUpload} 
        />

        <label 
          className="file-upload-label"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={triggerFileInput}
        >
          <div className="file-upload-label-icon">📤</div>
          <p>Drag and drop files here, or click to select</p>
          <p style={{fontSize: '0.8rem', color: '#6c757d'}}>
            Supported formats: PDF, DOCX
          </p>
        </label>
        
        {documents.length > 0 && (
          <div className="document-list">
            <h3>Uploaded Documents</h3>
            <ul>
              {documents.map((doc, index) => (
                <li key={index}>
                  <span>{doc.name}</span>
                  <div>
                    <span className="status">Pending Indexing</span>
                    <button 
                      onClick={() => removeDocument(index)}
                      style={{
                        marginLeft: '10px', 
                        background: 'none', 
                        border: 'none', 
                        color: '#e74c3c',
                        cursor: 'pointer'
                      }}
                    >
                      🗑️
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;
