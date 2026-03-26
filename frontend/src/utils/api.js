/**
 * CRI-RSK Chatbot — API utility.
 * Handles all communication with the FastAPI backend.
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://cri-ao-gpt-production.up.railway.app/api';
const API_BASE = API_BASE_URL;

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  const response = await fetch(url, config);
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error ${response.status}: ${error}`);
  }
  return response.json();
}

export async function sendMessage(message, agentType, conversationId = null) {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      agent_type: agentType,
      conversation_id: conversationId,
    }),
  });
}

export async function submitRating(messageId, score) {
  return request('/ratings', {
    method: 'POST',
    body: JSON.stringify({ message_id: messageId, score }),
  });
}

export async function generateOtp(dossierReference) {
  return request('/otp/generate', {
    method: 'POST',
    body: JSON.stringify({ dossier_reference: dossierReference }),
  });
}

export async function verifyOtp(dossierReference, otpCode) {
  return request('/otp/verify', {
    method: 'POST',
    body: JSON.stringify({
      dossier_reference: dossierReference,
      otp_code: otpCode,
    }),
  });
}

export async function healthCheck() {
  return request('/health');
}
