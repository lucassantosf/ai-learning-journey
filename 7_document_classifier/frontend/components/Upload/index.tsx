import React, { useState, useCallback } from 'react';
import styles from "../../styles/components/Upload.module.css";
import { apiService } from '../../services/api';  

// Define an interface for the upload result
interface UploadProps {
  onUploadComplete: (result: any) => void;
}

export default function Upload({ onUploadComplete }: UploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUploadTime, setLastUploadTime] = useState(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSave = useCallback(async () => {
    // Prevent multiple uploads within 2 seconds
    const currentTime = Date.now();
    if (currentTime - lastUploadTime < 2000) {
      console.warn('Upload blocked: Too frequent');
      return;
    }

    if (!file) {
      alert('Please select a file first');
      return;
    }

    setIsLoading(true);
    setLastUploadTime(currentTime);

    try {
      const result = await apiService.uploadDocument(file);
      onUploadComplete(result);
    } catch (error) {
      onUploadComplete({
        status: "error",
        content: error instanceof Error ? error.message : "Unknown error",
      });
    } finally {
      setIsLoading(false);
    }
  }, [file, lastUploadTime, onUploadComplete]);
 
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
          {isLoading ? (
            <>
              <span className={styles.spinner}></span>
              Uploading...
            </>
          ) : (
            "Save"
          )}
        </button>
      </div>
    </div>
  );
}
