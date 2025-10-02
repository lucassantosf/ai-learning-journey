import React, { useState } from 'react';
import styles from "../../styles/components/Upload.module.css";
import { apiService } from '../../services/api'; // We'll create this service

// Define an interface for the upload result
interface UploadResult {
  status: 'success' | 'error';
  predicted_class?: string;
  confidence?: number;
  extracted_data?: any;
  content?: string;
}

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      // Reset previous upload result when a new file is selected
      setUploadResult(null);
    }
  };

  const handleSave = async () => {
    if (!file) {
      alert('Please select a file first');
    }

    setIsLoading(true);
    setUploadResult(null);

    try {
      const result = await apiService.uploadDocument(file);
      setUploadResult(result);
    } catch (error) {
      setUploadResult({
        status: 'error',
        content: error instanceof Error ? error.message : 'An unknown error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderUploadResult = () => {
    if (!uploadResult) return null;

    return (
      <div className={styles.resultContainer}>
        <h3>Upload Result</h3>
        {uploadResult.status === 'success' ? (
          <div className={styles.successResult}>
            <p>Status: Success</p>
            <p>Document Type: {uploadResult.predicted_class}</p>
            <p>Confidence: {uploadResult.confidence?.toFixed(2)}%</p>
            <details>
              <summary>Extracted Data</summary>
              <pre>{JSON.stringify(uploadResult.extracted_data, null, 2)}</pre>
            </details>
          </div>
        ) : (
          <div className={styles.errorResult}>
            <p>Status: Error</p>
            <p>{uploadResult.content || 'Upload failed'}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={styles.container}>
      <div className={styles.uploadBox}>
        <input 
          type="file" 
          onChange={handleFileChange}
          className={styles.fileInput}
          accept=".pdf,.docx"
        />
        <button 
          onClick={handleSave}
          className={styles.saveButton}
          disabled={!file || isLoading}
        >
          {isLoading ? 'Uploading...' : 'Save'}
        </button>
      </div>
      {renderUploadResult()}
    </div>
  );
}