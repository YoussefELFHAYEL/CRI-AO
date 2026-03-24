import React, { useState, useRef, useEffect } from 'react';

export default function MessageInput({ onSend, disabled }) {
  const [text, setText] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text);
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const hasText = text.trim().length > 0;

  return (
    <form className="message-input" onSubmit={handleSubmit} id="message-input">
      <span className="input-icon" aria-label="Emoji">
        😊
      </span>
      <div className="input-field-wrapper">
        <input
          ref={inputRef}
          type="text"
          placeholder="Écrivez un message..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          id="chat-input"
        />
      </div>
      <button
        type={hasText ? 'submit' : 'button'}
        className="send-btn"
        disabled={disabled && hasText}
        id="send-btn"
        aria-label={hasText ? 'Envoyer' : 'Microphone'}
      >
        {hasText ? '➤' : '🎤'}
      </button>
    </form>
  );
}
