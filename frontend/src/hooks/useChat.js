/**
 * CRI-RSK Chatbot — useChat hook.
 * Manages chat state, message sending, and conversation flow.
 */

import { useState, useCallback, useRef } from 'react';
import { sendMessage } from '../utils/api.js';

const WELCOME_MESSAGES = {
  public: {
    fr: "Bonjour ! 👋 Que souhaitez-vous faire ?",
    buttons: [
      { label: "Informations et procédures", value: "Je cherche des informations sur l’investissement à Rabat dans le domaine industriel.", emoji: "1️⃣" },
      { label: "Incitations et aides", value: "Quelles sont les incitations ?", emoji: "2️⃣" },
      { label: "Suivre mon dossier", value: "Je voudrais suivre mon dossier", emoji: "3️⃣" },
      { label: "Parler à un agent", value: "Je veux parler à un agent humain", emoji: "4️⃣" }
    ]
  },
  internal: {
    fr: "Bienvenue sur le portail interne CRI-RSK 🔐. Que souhaitez-vous faire ?",
    buttons: [
      { label: "Tableau de bord", value: "Tableau de bord", emoji: "📊" },
      { label: "Dossiers en attente", value: "Dossiers en attente", emoji: "⏳" }
    ]
  },
};

function createWelcomeMessage(agentType) {
  const config = WELCOME_MESSAGES[agentType] || WELCOME_MESSAGES.public;
  return {
    id: `welcome-${agentType}`,
    role: 'bot',
    content: config.fr,
    buttons: config.buttons || null,
    timestamp: new Date(),
    language: 'fr',
  };
}

export function useChat({ onNotify } = {}) {
  const [messages, setMessages] = useState({
    public: [createWelcomeMessage('public')],
    internal: [createWelcomeMessage('internal')],
  });
  const [agentType, setAgentType] = useState(null);
  const [conversationIds, setConversationIds] = useState({
    public: null,
    internal: null,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [ratings, setRatings] = useState({});
  const abortRef = useRef(null);

  const currentMessages = messages[agentType] || [];

  const addMessage = useCallback((msg) => {
    setMessages((prev) => ({
      ...prev,
      [agentType]: [...(prev[agentType] || []), msg],
    }));
  }, [agentType]);

  const send = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    // Add user message locally
    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };
    addMessage(userMsg);
    setIsLoading(true);

    try {
      const response = await sendMessage(
        text.trim(),
        agentType,
        conversationIds[agentType]
      );

      // Store conversation ID
      if (response.conversation_id) {
        setConversationIds((prev) => ({
          ...prev,
          [agentType]: response.conversation_id,
        }));
      }

      // Trigger persistent notification if an OTP code is returned
      if (response.otp_code && onNotify) {
        onNotify(`🔐 Votre code OTP est : ${response.otp_code}`, true);
      }

      // Add bot response
      const botMsg = {
        id: response.message_id || `bot-${Date.now()}`,
        role: 'bot',
        content: response.response,
        timestamp: new Date(),
        language: response.language,
        buttons: response.buttons || null,
        isEscalation: response.is_escalation || false,
        isFallback: response.is_fallback || false,
      };
      addMessage(botMsg);
    } catch (error) {
      console.error('Chat error:', error);
      const errorContent = "Désolé, une erreur s'est produite. Veuillez réessayer.";
        
      const errorMsg = {
        id: `error-${Date.now()}`,
        role: 'bot',
        content: errorContent,
        timestamp: new Date(),
        isError: true,
      };
      addMessage(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [agentType, conversationIds, isLoading, addMessage]);

  const switchAgent = useCallback((newAgent) => {
    setAgentType(newAgent);
    // Initialize with welcome message if empty
    setMessages((prev) => {
      if (!prev[newAgent] || prev[newAgent].length === 0) {
        return {
          ...prev,
          [newAgent]: [createWelcomeMessage(newAgent)],
        };
      }
      return prev;
    });
  }, []);

  const rateMessage = useCallback((messageId, score) => {
    setRatings((prev) => ({ ...prev, [messageId]: score }));
  }, []);

  const addNotification = useCallback((text) => {
    const notifMsg = {
      id: `notif-${Date.now()}`,
      role: 'bot',
      content: text,
      timestamp: new Date(),
      isNotification: true,
    };
    addMessage(notifMsg);
  }, [addMessage]);

  return {
    messages: currentMessages,
    allMessages: messages,
    agentType,
    isLoading,
    ratings,
    send,
    switchAgent,
    rateMessage,
    addNotification,
    conversationId: conversationIds[agentType],
  };
}
