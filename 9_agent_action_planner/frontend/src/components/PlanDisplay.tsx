import React, { useState } from 'react'
import styles from './PlanDisplay.module.css'

interface PlanStep {
  description: string
  completed: boolean
}

const PlanDisplay: React.FC = () => {
  const [plan, setPlan] = useState<PlanStep[]>([
    { description: 'Research destination', completed: false },
    { description: 'Create travel itinerary', completed: false },
    { description: 'Book flights', completed: false },
    { description: 'Reserve accommodation', completed: false }
  ])

  const toggleStepCompletion = (index: number) => {
    const updatedPlan = [...plan]
    updatedPlan[index].completed = !updatedPlan[index].completed
    setPlan(updatedPlan)
  }

  return (
    <div className={styles['plan-container']}>
      <h2 className={styles['plan-title']}>Action Plan</h2>
      <ul className={styles['plan-list']}>
        {plan.map((step, index) => (
          <li 
            key={index} 
            className={styles['plan-item']}
            onClick={() => toggleStepCompletion(index)}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 20 20" 
              fill="currentColor" 
              className={`${styles['plan-item-icon']} ${
                step.completed ? styles['plan-item-completed'] : ''
              }`}
            >
              {step.completed ? (
                <path 
                  fillRule="evenodd" 
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" 
                  clipRule="evenodd" 
                />
              ) : (
                <path 
                  d="M10 18a8 8 0 100-16 8 8 0 000 16z" 
                />
              )}
            </svg>
            <span>{step.description}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default PlanDisplay
