import React, { useState } from 'react'
import ChallengeInput from '../../components/ChallengeInput'
import PlanDisplay from '../../components/PlanDisplay'

export default function Home() {
  const [currentPlan, setCurrentPlan] = useState<{
    plan_id: number;
    status: string;
    steps: string[];
  } | null>(null);

  const handlePlanCreated = (plan: {
    plan_id: number;
    status: string;
    steps: string[];
  }) => {
    setCurrentPlan(plan);
  };

  return (
    <div className="container" style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '2rem',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '2rem'
    }}>
      <header style={{ 
        textAlign: 'center', 
        maxWidth: '800px'
      }}>
        <h1 style={{ 
          color: 'var(--primary-color)', 
          fontSize: '2.5rem',
          marginBottom: '1rem'
        }}>
          AI Action Planner
        </h1>
        <p style={{
          color: 'var(--text-color)',
          fontSize: '1.1rem',
          lineHeight: '1.6',
          textAlign: 'center'
        }}>
          Transform your challenges into actionable plans with our AI-powered planning assistant. 
          Enter a problem or goal, and watch as our intelligent agent breaks it down into 
          manageable, step-by-step actions.
        </p>
      </header>

      <main style={{
        width: '100%',
        maxWidth: '800px',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem'
      }}>
        <section>
          <ChallengeInput onPlanCreated={handlePlanCreated} />
        </section>

        <section>
          {currentPlan && <PlanDisplay plan={currentPlan} />}
        </section>
      </main>

      <footer style={{
        marginTop: '2rem',
        textAlign: 'center',
        color: 'var(--text-color)',
        opacity: 0.7
      }}>
        <p>
          Powered by AI | Simplifying Complex Challenges
        </p>
      </footer>
    </div>
  )
}