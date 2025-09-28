import Header from "../components/Header";
import HealthChecker from "../components/HealthCheck";
import styles from "../styles/pages/healthcheck.module.css";

export default function HealthCheck() {
  return (
    <div className={styles.container}>
      <Header 
        title="Healthcheck" 
        pageTitle="Health Check" 
        description="Check how is the backend's health" 
      />
      <HealthChecker />
    </div> 
  );
}