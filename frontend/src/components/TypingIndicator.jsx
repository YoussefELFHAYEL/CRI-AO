import React from 'react';

export default function TypingIndicator() {
  return (
    <div className="skeleton-loader" id="typing-indicator">
      <div className="skeleton-line full" />
      <div className="skeleton-line medium" />
      <div className="skeleton-line short" />
    </div>
  );
}
