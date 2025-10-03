import React, { useState } from 'react';
import styles from "../../styles/components/Upload.module.css";
import { apiService } from '../../services/api';  

// Define an interface for the upload result
interface UploadProps {
  onUploadComplete: (result: any) => void;
}

export default function Upload({ onUploadComplete }: UploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSave = async () => {
    if (!file) {
      alert('Please select a file first');
    }

    setIsLoading(true);

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