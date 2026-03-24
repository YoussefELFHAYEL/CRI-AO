import React, { useState, useEffect } from 'react';

export default function NotificationBanner({ text, persistent = false, onDismiss }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    if (persistent) return; // Skip auto-dismiss if persistent

    const timer = setTimeout(() => {
      setVisible(false);
      if (onDismiss) onDismiss();
    }, 5000);
    return () => clearTimeout(timer);
  }, [onDismiss, persistent]);

  if (!visible) return null;

  return (
    <div className="notification-banner" id="notification-banner" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 20px' }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <span className="notif-icon" style={{ marginRight: '10px' }}>🔔</span>
        <span style={{ whiteSpace: 'pre-wrap' }}>{text}</span>
      </div>
      <button 
        onClick={() => { setVisible(false); if(onDismiss) onDismiss(); }}
        style={{ cursor: 'pointer', background: 'transparent', border: 'none', fontSize: '1.5rem', color: 'inherit', marginLeft: '15px' }}
      >
        &times;
      </button>
    </div>
  );
}
