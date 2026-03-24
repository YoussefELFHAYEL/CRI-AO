import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble.jsx';
import TypingIndicator from './TypingIndicator.jsx';

export default function ChatWindow({
  messages,
  isLoading,
  ratings,
  onRate,
  onButtonSelect,
}) {
  const bottomRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="chat-window" id="chat-window">
      
      {/* Fake Date Separator (WhatsApp Style) */}
      <div style={{ display: 'flex', justifyContent: 'center', margin: '10px 0' }}>
        <span style={{
          background: '#e9edef', padding: '5px 12px', borderRadius: '8px',
          fontSize: '12px', color: '#54656f', textAlign: 'center'
        }}>
          Aujourd'hui
        </span>
      </div>

      {messages.map((msg) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          rating={ratings[msg.id]}
          onRate={onRate}
          onButtonSelect={onButtonSelect}
        />
      ))}

      {isLoading && (
        <div style={{ alignSelf: 'flex-start', background: '#ffffff', borderRadius: '0 8px 8px 8px', padding: '12px' }}>
          <TypingIndicator />
        </div>
      )}

      <div ref={bottomRef} style={{ height: '1px' }} />
    </div>
  );
}
