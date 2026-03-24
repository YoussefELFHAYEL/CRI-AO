import React from 'react';

export default function Sidebar({ agentType, onSwitch, messages }) {
  // Extract last messages if available
  const publicMsgList = messages?.public || [];
  const internalMsgList = messages?.internal || [];

  const lastPublicMsg = publicMsgList.length > 0 ? publicMsgList[publicMsgList.length - 1] : null;
  const lastInternalMsg = internalMsgList.length > 0 ? internalMsgList[internalMsgList.length - 1] : null;

  const formatTime = (dateObj) => {
    if (!dateObj) return '';
    const date = new Date(dateObj);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const truncate = (text) => {
    if (!text) return '';
    return text.length > 35 ? text.substring(0, 35) + '...' : text;
  };

  return (
    <div className="sidebar">
      {/* SECTION 1 - Header Sidebar */}
      <div className="sidebar-header">
        <div className="sidebar-avatar">
          {/* Logo Placeholder */}
          🏛️
        </div>
        <div className="sidebar-icons">
          <span>⭕</span>
          <span>🔍</span>
          <span>⋮</span>
        </div>
      </div>

      {/* SECTION 2 - Barre de recherche */}
      <div className="sidebar-search">
        <div className="search-input-wrapper">
          <span style={{color: '#54656f', fontSize: '18px'}}>🔍</span>
          <input type="text" placeholder="Rechercher ou démarrer une discussion" />
        </div>
      </div>

      {/* SECTION 3 - Liste des contacts */}
      <div className="sidebar-contacts">
        
        {/* Contact 1 : Agent Public */}
        <div 
          className={`contact-item ${agentType === 'public' ? 'active' : ''}`}
          onClick={() => onSwitch('public')}
        >
          <div className="contact-avatar">
            🏢
          </div>
          <div className="contact-info">
            <div className="contact-header">
              <span className="contact-name">CRI-RSK Assistant Public</span>
              <span className="contact-time">{formatTime(lastPublicMsg?.timestamp)}</span>
            </div>
            <div className="contact-sub">
              <span className="contact-preview">
                {lastPublicMsg ? truncate(lastPublicMsg.content) : "Porteurs de projets & Usagers"}
              </span>
            </div>
          </div>
        </div>

        {/* Separator */}
        <div className="contact-separator">
          ASSISTANTS CRI-RSK
        </div>

        {/* Contact 2 : Agent Interne */}
        <div 
          className={`contact-item ${agentType === 'internal' ? 'active' : ''}`}
          onClick={() => onSwitch('internal')}
        >
          <div className="contact-avatar" style={{background: '#f8d7da'}}>
            🔐
          </div>
          <div className="contact-info">
            <div className="contact-header">
              <span className="contact-name">
                Agent Interne
                <span className="internal-badge">🔐 Interne</span>
              </span>
              <span className="contact-time">{formatTime(lastInternalMsg?.timestamp)}</span>
            </div>
            <div className="contact-sub">
              <span className="contact-preview">
                {lastInternalMsg ? truncate(lastInternalMsg.content) : "Collaborateurs CRI - Accès restreint"}
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
