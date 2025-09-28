import React from "react";
import Header from "../components/Header";
import Upload from "../components/Upload"
import Link from "next/link";
import styles from "../styles/pages/Index.module.css";

export default function Home() {
  return (
    <div className={styles.container}>
      <Header />
      <main className={styles.main}>
        <div className={styles.featuredActions}>
          <div className={styles.actionCard}>
            <Upload />
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
      </main>
    </div>
  );
}
