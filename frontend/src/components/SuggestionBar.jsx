import React from 'react';

const PUBLIC_SUGGESTIONS = [
  { label: '❓ FAQ', value: 'Quels sont les différents délais de dépôt et de traitement du recours ?' },
  { label: '💰 Incitations', value: 'Quelles sont les incitations à l\'investissement ?' },
  { label: '📋 Suivre dossier', value: 'Je voudrais suivre mon dossier INV-2024-001' },
  { label: '❔ Question', value: 'quelles sont les incitations pour AMÉLIORATION DE LA LA COMPÉTITIVITÉ DES ENTREPRISES GIAC Hôtellerie et tourisme ?' },
  { label: '🌍 Hello', value: 'Hello, I\'d like information about investing' },
  { label: '🇲🇦 مرحبا', value: 'مرحبا، أريد معلومات عن الاستثمار' },
];

const INTERNAL_SUGGESTIONS = [
  { label: '📊 Tableau de bord', value: 'Tableau de bord statistiques du jour' },
  { label: '⏳ En attente', value: 'Afficher les dossiers en attente' },
  { label: '✅ Validés', value: 'Afficher les dossiers validés' },
  { label: '📈 Rapport', value: 'Générer un rapport de synthèse' },
  { label: '🔍 INV-2024-001', value: 'Dossier INV-2024-001' },
];

export default function SuggestionBar({ agentType, onSelect }) {
  const suggestions = agentType === 'internal' ? INTERNAL_SUGGESTIONS : PUBLIC_SUGGESTIONS;

  return (
    <div className="suggestion-bar" id="suggestion-bar">
      {suggestions.map((s, i) => (
        <button
          key={i}
          className="suggestion-chip"
          onClick={() => onSelect(s.value)}
          id={`suggestion-${i}`}
        >
          {s.label}
        </button>
      ))}
    </div>
  );
}
