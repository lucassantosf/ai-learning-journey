import Header from "../components/Header";
import Upload from "../components/Upload"
import Link from "next/link";
import { useState } from "react";
import { apiGet } from "../services/api";
import styles from "../styles/pages/Index.module.css";

export default function Home() {
  const [health, setHealth] = useState<any>(null);

  async function checkHealth() {
    try {
      const data = await apiGet("/health");
      setHealth(data);
    } catch (err: any) {
      setHealth({ error: err.message });
    }
  }

  return (
    <div className={styles.container}>
      <Header />
      <Upload />
      <Link href="/about" className={styles.link}>Go to About Page</Link>

      <button onClick={checkHealth} className={styles.healthButton}>
        Checar Backend
      </button>

      {health && (
        <pre className={styles.healthOutput}>
          {JSON.stringify(health, null, 2)}
        </pre>
      )}
    </div>
  );
}
