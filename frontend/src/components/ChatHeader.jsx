import React from 'react';

export default function ChatHeader({ agentType, onBack }) {
  const isInternal = agentType === 'internal';

  return (
    <div className="chat-header" id="chat-header">
      <div className="chat-header-profile">
        <button className="back-btn" onClick={onBack}>←</button>
        <div className="chat-header-avatar" style={isInternal ? {background: '#f8d7da'} : {}}>
          {isInternal ? '🔐' : '🏢'}
        </div>
        <div className="chat-header-info">
          <span className="chat-header-name">
            {isInternal ? 'CRI-RSK Agent Interne' : 'CRI-RSK Assistant Public'}
          </span>
          <span className="chat-header-status status-online">En ligne</span>
        </div>
      </div>
      <div className="chat-header-icons">
        <span>🔍</span>
        <span>⋮</span>
      </div>
    </div>
  );
}
