import React, { useState } from 'react';
import styles from "../../styles/components/Upload.module.css";

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSave = () => {
    if (file) {
      alert(`File selected: ${file.name}`);
    } else {
      alert('Please select a file first');
    }
  };

  return (
    <>
      <div className={styles.container}>
        <div className={styles.uploadBox}>
          <input 
            type="file" 
            onChange={handleFileChange}
            className={styles.fileInput}
          />
          <button 
            onClick={handleSave}
            className={styles.saveButton}
          >
            Save
          </button>
        </div>
      </div>
    </>
  );
}