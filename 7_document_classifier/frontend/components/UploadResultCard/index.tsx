import React from "react";
import styles from "../../styles/components/UploadResultCard.module.css";

interface UploadResultProps {
  result: {
    status: "success" | "error";
    predicted_class?: string;
    confidence?: number;
    extracted_data?: any;
    content?: string;
  };
}

export default function UploadResultCard({ result }: UploadResultProps) {
  return (
    <div className={styles.container}>
      <h3>Upload Result</h3>
      {result.status === "success" ? (
        <div className={styles.successResult}>
          <p>Status: ✅ Success</p>
          <p>Document Type: {result.predicted_class}</p>
          <p>Confidence: {result.confidence?.toFixed(2)}%</p>
          <details open>
            <summary>Extracted Data</summary>
            <pre>{JSON.stringify(result.extracted_data, null, 2)}</pre>
          </details>
        </div>
      ) : (
        <div className={styles.errorResult}>
          <p>Status: ❌ Error</p>
          <p>{result.content || "Upload failed"}</p>
        </div>
      )}
    </div>
  );
}
