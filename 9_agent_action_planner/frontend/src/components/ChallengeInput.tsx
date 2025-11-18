import React, { useState } from 'react'
import styles from './ChallengeInput.module.css'

const ChallengeInput: React.FC = () => {
  const [challenge, setChallenge] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (challenge.trim()) {
      // TODO: Implement challenge submission logic
      console.log('Challenge submitted:', challenge)
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles['challenge-input-container']}>
      <div className={styles['challenge-input']}>
        <input 
          type="text"
          value={challenge}
          onChange={(e) => setChallenge(e.target.value)}
          placeholder="Enter your challenge or problem..."
          className="input-field"
        />
      </div>
      <div className={styles['challenge-submit']}>
        <button 
          type="submit" 
          className="btn btn-primary"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            strokeWidth={1.5} 
            stroke="currentColor" 
            className={styles['challenge-submit-icon']}
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 9.5a59.768 59.768 0 0 1-2.216 8.875c-.254.625-.542 1.24-.854 1.845a9.76 9.76 0 0 1-.245.5 7.608 7.608 0 0 1-.715 1.227 8.974 8.974 0 0 1-1.658 1.785c-.757.65-1.7 1.1-2.729 1.1-1.717 0-3.224-1.265-3.636-3.005l-1.5-6.434-1.5 6.434C7.224 20.735 5.717 22 4 22c-1.03 0-1.973-.45-2.73-1.1a8.976 8.976 0 0 1-1.658-1.785 7.617 7.617 0 0 1-.715-1.227 9.758 9.758 0 0 1-.245-.5 59.441 59.441 0 0 1-.854-1.845A59.769 59.769 0 0 1 2.515 9.5a59.77 59.77 0 0 1 18.216 0" 
            />
          </svg>
          Launch
        </button>
      </div>
    </form>
  )
}

export default ChallengeInput
