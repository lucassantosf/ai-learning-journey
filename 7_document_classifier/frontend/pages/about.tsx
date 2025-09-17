import AboutMe from "../components/AboutMe";
import Link from "next/link";

export default function About() {
  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <AboutMe />
      <Link href="/">Back to Home</Link>
    </div>
  );
}