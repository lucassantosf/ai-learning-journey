import HelloWorld from "../components/HelloWorld";
import Link from "next/link";
import { useState } from "react";
import { apiGet } from "../services/api";

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
    <div style={{ padding: "20px", textAlign: "center" }}>
      <HelloWorld />
      <Link href="/about">Go to About Page</Link>

      <button onClick={checkHealth}>Checar Backend</button>

      {health && (
        <pre style={{ marginTop: "1rem", background: "#f4f4f4", padding: "1rem" }}>
          {JSON.stringify(health, null, 2)}
        </pre>
      )}
    </div>
  );
}
