import React, { useState } from 'react';
import { useChat } from '../hooks/useChat.js';
import Sidebar from '../components/Sidebar.jsx';
import ChatHeader from '../components/ChatHeader.jsx';
import ChatWindow from '../components/ChatWindow.jsx';
import SuggestionBar from '../components/SuggestionBar.jsx';
import MessageInput from '../components/MessageInput.jsx';
import DemoPanel from '../components/DemoPanel.jsx';
import NotificationBanner from '../components/NotificationBanner.jsx';

export default function ChatView() {
  const [notification, setNotification] = useState(null);

  const {
    messages,
    allMessages,
    agentType,
    isLoading,
    ratings,
    send,
    switchAgent,
    rateMessage,
    addNotification,
  } = useChat({
    onNotify: (text, persistent = false) => {
      setNotification({ text, persistent, id: Date.now() });
    }
  });

  const handleSend = (text) => {
    send(text);
  };

  const handleSuggestion = (text) => {
    send(text);
  };

  const handleButtonSelect = (value) => {
    send(value);
  };

  const notifyFromDemo = (text) => {
    setNotification({ text, persistent: false, id: Date.now() });
    addNotification(text);
  };

  return (
    <div className={`app-container ${agentType ? 'chat-active' : ''}`} id="app-container">
      
      {/* 1. Sidebar (Contacts) */}
      <Sidebar 
        agentType={agentType} 
        onSwitch={switchAgent} 
        messages={allMessages} 
      />

      {/* 2. Main Chat Area */}
      <div className="main-chat">
        {!agentType ? (
          <div className="empty-state">
            <h1>CRI-RSK Chatbot</h1>
            <p>Sélectionnez un assistant dans le menu de gauche pour démarrer.</p>
            <p style={{fontSize: '12px', marginTop: '10px'}}>Centre Régional d'Investissement de Rabat-Salé-Kénitra</p>
          </div>
        ) : (
          <>
            <ChatHeader agentType={agentType} onBack={() => switchAgent(null)} />
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              ratings={ratings}
              onRate={rateMessage}
              onButtonSelect={handleButtonSelect}
            />
            <SuggestionBar agentType={agentType} onSelect={handleSuggestion} />
            <MessageInput onSend={handleSend} disabled={isLoading} />
          </>
        )}
      </div>

      {/* 3. Demo Panel (right side) */}
      <DemoPanel
        onRunScenario={handleSend}
        onNotify={notifyFromDemo}
        currentAgent={agentType}
        onSwitchAgent={switchAgent}
      />

      {/* Notification Banner */}
      {notification && (
        <NotificationBanner
          key={notification.id}
          text={notification.text}
          persistent={notification.persistent}
          onDismiss={() => setNotification(null)}
        />
      )}
    </div>
  );
}
