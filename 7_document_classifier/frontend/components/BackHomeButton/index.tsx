import React from "react";
import styles from "../../styles/components/BackHomeButton.module.css";
import Link from "next/link";

export default function BackHomeButton() {
  return (
    <>
      <Link href="/" className={styles.link}>
        Back to Home
      </Link>
    </>
  );
}