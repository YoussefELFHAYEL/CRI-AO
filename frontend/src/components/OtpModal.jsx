import React, { useState } from 'react';

export default function OtpModal({ dossierRef, demoOtp, onVerify, onClose }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = () => {
    if (code.length !== 6) {
      setError('Le code doit contenir 6 chiffres');
      return;
    }
    onVerify(code);
  };

  return (
    <div className="otp-modal-overlay" onClick={onClose} id="otp-modal">
      <div className="otp-modal" onClick={(e) => e.stopPropagation()}>
        <h3>🔒 Vérification OTP</h3>
        <p>
          Un code de vérification a été généré pour le dossier{' '}
          <strong>{dossierRef}</strong>. Entrez le code à 6 chiffres.
        </p>
        <div className="otp-input-group">
          <input
            type="text"
            className="otp-input"
            maxLength={6}
            value={code}
            onChange={(e) => {
              setCode(e.target.value.replace(/[^0-9]/g, ''));
              setError('');
            }}
            placeholder="000000"
            autoFocus
            id="otp-input"
          />
        </div>
        {error && (
          <div style={{ color: '#DC2626', fontSize: 13, marginBottom: 12 }}>
            {error}
          </div>
        )}
        <div className="otp-modal-actions">
          <button className="otp-btn secondary" onClick={onClose}>
            Annuler
          </button>
          <button className="otp-btn primary" onClick={handleSubmit} id="otp-verify-btn">
            Vérifier
          </button>
        </div>
        {demoOtp && (
          <div className="otp-demo-hint">
            🎭 Mode démo — Code OTP:{' '}
            <span className="otp-demo-code">{demoOtp}</span>
          </div>
        )}
      </div>
    </div>
  );
}
