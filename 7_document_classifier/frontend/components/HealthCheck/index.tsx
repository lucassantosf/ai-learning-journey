import React, { useState } from "react";
import styles from "../../styles/components/HealthCheck.module.css";
import { apiGet } from "../../services/api";
import Link from "next/link";

export default function HealthChecker() {
  const [health, setHealth] = useState<{ status?: number; error?: string } | null>(null);

  async function checkHealth() {
    try {
      const data = await apiGet("/health");
      setHealth({ status: 200 });
    } catch (err: any) {
      setHealth({ status: 500, error: err.message });
    }
  }

  const isHealthy = health?.status === 200;

  return (
    <div className={styles.container}>
      <button 
        onClick={checkHealth} 
        className={`${styles.healthButton} ${
          health ? (isHealthy ? styles.healthyButton : styles.errorButton) : ''
        }`}
      >
        Checar Backend
      </button>

      {health && (
        <div className={`${styles.statusIndicator} ${isHealthy ? styles.healthy : styles.error}`}>
          {isHealthy ? '✅ Backend is Online' : '❌ Backend is Offline'}
        </div>
      )}

      <Link href="/" className={styles.link}>
        Back to Home
      </Link>
    </div>
  );
}