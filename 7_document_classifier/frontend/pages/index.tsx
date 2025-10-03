import React, { useState } from "react";
import Header from "../components/Header";
import Upload from "../components/Upload";
import UploadResultCard from "../components/UploadResultCard";
import Link from "next/link";
import styles from "../styles/pages/Index.module.css";

export default function Home() {
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  
  return (
    <div className={styles.container}>
      <Header />
      <main className={styles.main}>
        {/* Linha 1 */}
        <div className={styles.featuredActions}>
          <div className={styles.actionCard}>
            <Upload onUploadComplete={setUploadResult}/>
          </div>

          <div className={styles.actionCard}>
            <Link href="/healthcheck" className={styles.healthCheckLink}>
              <div className={styles.cardContent}>
                <span>🩺</span>
                <h3>Backend Health Check</h3>
                <p>Verify system connectivity and status</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Linha 2 - só aparece depois do upload */}
        
        {uploadResult && (
          <div className={styles.resultRow}>
            <div className={styles.actionCard}>
              <UploadResultCard result={uploadResult} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
