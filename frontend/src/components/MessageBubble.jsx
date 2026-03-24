import React from 'react';
import { isRtlText } from '../utils/rtl.js';
import ButtonGroup from './ButtonGroup.jsx';
import Rating from './Rating.jsx';

function formatTime(date) {
  if (!date) return '';
  const d = date instanceof Date ? date : new Date(date);
  return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

function formatContent(text) {
  if (!text) return text;
  // Bold: **text** → <strong>text</strong>
  let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Markdown links fallback
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:#027eb5;">$1</a>');
  // Newlines
  html = html.replace(/\n/g, '<br/>');
  return html;
}

export default function MessageBubble({
  message,
  rating,
  onRate,
  onButtonSelect,
}) {
  const { id, role, content, timestamp, buttons, isNotification, isError } = message;
  const isUser = role === 'user';
  const isBot = role === 'bot';
  const rtl = isRtlText(content);

  let bubbleClass = `message-bubble message-${role}`;
  if (isError) bubbleClass += ' message-error';
  // Note: RTL logic is handled via direction CSS or manually
  
  return (
    <div
      className={bubbleClass}
      id={`msg-${id}`}
      style={{ direction: rtl ? 'rtl' : 'ltr', textAlign: rtl ? 'right' : 'left' }}
    >
      {isNotification && (
        <div style={{ fontSize: '11px', color: '#92400E', marginBottom: 4, fontWeight: 600 }}>
          🔔 Notification
        </div>
      )}
      <div
        className="message-content"
        dangerouslySetInnerHTML={{ __html: formatContent(content) }}
      />

      {buttons && buttons.length > 0 && (
        <ButtonGroup buttons={buttons} onSelect={onButtonSelect} />
      )}

      {/* Timestamp inline floating right */}
      <div className="message-timestamp">
        <span>{formatTime(timestamp)}</span>
        {isUser && <span style={{ marginLeft: '4px', color: '#53bdeb' }}>✓✓</span>}
      </div>

      <div style={{ clear: 'both' }}></div>

      {isBot && !message.isError && !isNotification && id && !id.startsWith('welcome') && (
        <div style={{ marginTop: '10px', fontSize: '12px' }}>
          <hr style={{ border: 'none', borderTop: '1px solid #e9edef', margin: '5px 0' }} />
          <Rating messageId={id} currentRating={rating} onRate={onRate} />
        </div>
      )}
    </div>
  );
}
