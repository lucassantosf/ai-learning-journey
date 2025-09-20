import React from "react";
import Head from 'next/head';
import styles from "../../styles/components/Header.module.css";

interface HeaderProps {
  title?: string;
  pageTitle?: string;
  description?: string;
}

export default function Header({ 
  title = "Classificador de Documentos🚀", 
  pageTitle, 
  description = "Classificador inteligente de documentos (contratos, currículos, notas fiscais)" 
}: HeaderProps) {
  return (
    <>
      <Head>
        <title>{pageTitle || title}</title>
      </Head>
      <div className={styles.container}>
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.description}>{description}</p>
      </div>
    </>
  );
}