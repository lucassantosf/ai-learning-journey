import React from "react";
import styles from "../../styles/components/About.module.css";

export default function AboutMe() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Developed By</h1>
      <p className={styles.description}>Essa é a segunda página do projeto.</p>
    </div>
  );
}