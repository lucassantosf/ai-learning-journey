import Header from "../components/Header";
import AboutMe from "../components/AboutMe";
import Link from "next/link";
import styles from "../styles/pages/About.module.css";

export default function About() {
  return (
    <div className={styles.container}>
      <Header 
        title="About Page" 
        pageTitle="About Me" 
        description="Learn more about our document classification project" 
      />
      <AboutMe />
      <Link href="/" className={styles.link}>
        Back to Home
      </Link>
    </div> 
  );
}