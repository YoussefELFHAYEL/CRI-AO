import React from 'react';

export default function ButtonGroup({ buttons, onSelect }) {
  if (!buttons || buttons.length === 0) return null;

  return (
    <div className="button-group">
      {buttons.map((btn, idx) => (
        <button
          key={idx}
          className="action-btn"
          onClick={() => onSelect(btn.value || btn.label)}
          id={`wa-btn-${idx}`}
        >
          {btn.emoji && <span>{btn.emoji}</span>}
          {btn.label}
        </button>
      ))}
    </div>
  );
}
