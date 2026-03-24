import React from 'react';

export default function AgentSelector({ agentType, onSwitch }) {
  return (
    <div className="agent-selector" id="agent-selector">
      <button
        className={agentType === 'public' ? 'active' : ''}
        onClick={() => onSwitch('public')}
        id="agent-btn-public"
      >
        👥 Agent Public
      </button>
      <button
        className={`${agentType === 'internal' ? 'active internal-active' : ''}`}
        onClick={() => onSwitch('internal')}
        id="agent-btn-internal"
      >
        🔐 Agent Interne
      </button>
    </div>
  );
}
