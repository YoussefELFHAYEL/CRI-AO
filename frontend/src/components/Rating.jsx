import React, { useState } from 'react';
import { submitRating } from '../utils/api.js';

export default function Rating({ messageId, currentRating, onRate }) {
  const [hoveredStar, setHoveredStar] = useState(0);
  const [submitted, setSubmitted] = useState(!!currentRating);

  const handleClick = async (score) => {
    if (submitted) return;
    onRate(messageId, score);
    setSubmitted(true);
    try {
      await submitRating(messageId, score);
    } catch (err) {
      console.error('Rating submit error:', err);
    }
  };

  const isActive = (star) => star <= (hoveredStar || currentRating || 0);

  return (
    <div className="rating-container" id={`rating-${messageId}`}>
      <span className="rating-label">Évaluer :</span>
      <div className="rating-stars">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            className={`rating-star ${
              isActive(star) ? 'active' : ''
            } ${submitted ? 'submitted' : ''}`}
            onClick={() => handleClick(star)}
            onMouseEnter={() => !submitted && setHoveredStar(star)}
            onMouseLeave={() => !submitted && setHoveredStar(0)}
            disabled={submitted}
            aria-label={`${star} étoile${star > 1 ? 's' : ''}`}
          >
            {isActive(star) ? '★' : '☆'}
          </button>
        ))}
      </div>
    </div>
  );
}
