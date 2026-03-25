import React, { useState } from 'react';

const DOSSIERS_DEMO = [
  { ref: 'INV-2024-001', desc: 'Restaurant - En cours 🔄' },
  { ref: 'INV-2024-002', desc: 'Centre Form. - Validé ✅' },
  { ref: 'INV-2024-003', desc: 'Usine - En attente ⏳' },
  { ref: 'INV-2024-004', desc: 'E-com - Rejeté ❌' },
];

export default function DemoPanel({
  onRunScenario,
  onNotify,
  currentAgent,
  onSwitchAgent,
}) {
  const [playingId, setPlayingId] = useState(null);
  const [expandedSection, setExpandedSection] = useState('dossiers');

  const runScenario = async (id, messages, targetAgent = 'public') => {
    setPlayingId(id);

    // Switch agent if needed
    if (targetAgent && targetAgent !== currentAgent) {
      onSwitchAgent(targetAgent);
      await new Promise((r) => setTimeout(r, 400));
    }

    // Send each message in sequence
    for (const msg of messages) {
      onRunScenario(msg);
      await new Promise((r) => setTimeout(r, 600));
    }

    setTimeout(() => setPlayingId(null), 1000);
  };

  const handleNotify = () => {
    onNotify(
      '🔔 **CRI-RSK ALERTE** 🔔\n\n' +
      'Votre dossier d\'investissement **INV-2024-002** vient de changer de statut !\n\n' +
      '• **Nouveau statut** : Approuvé ✅\n' +
      '• **Date** : Aujourd\'hui à 11h30\n\n' +
      'Vous pouvez télécharger votre attestation d\'approbation sur votre portail.'
    );
  };

  const toggleSection = (sec) => {
    setExpandedSection(expandedSection === sec ? null : sec);
  };

  const SectionHeader = ({ id, icon, title }) => (
    <div 
      style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        background: '#2d3f50', padding: '10px', borderRadius: '8px',
        cursor: 'pointer', marginBottom: '8px', color: 'white', fontSize: '14px',
        borderLeft: expandedSection === id ? '4px solid #00a884' : '4px solid transparent'
      }}
      onClick={() => toggleSection(id)}
    >
      <span>{icon} {title}</span>
      <span style={{ fontSize: '10px' }}>{expandedSection === id ? '▼' : '▶'}</span>
    </div>
  );

  return (
    <div className="demo-panel" id="demo-panel" style={{ overflowY: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <div className="demo-panel-header" style={{ marginBottom: '15px' }}>
        <h3 style={{ fontSize: '16px', color: 'white' }}>🎯 Fonctionnalités</h3>
        <p style={{ fontSize: '12px', color: '#8c9eae' }}>Données de démo disponibles</p>
      </div>

      <div className="demo-scenarios" style={{ flex: 1, overflowY: 'auto', paddingRight: '5px' }}>

        {/* 1. Suivi de Dossiers */}
        <SectionHeader id="dossiers" icon="📋" title="Suivi Dossiers (OTP)" />
        {expandedSection === 'dossiers' && (
          <div style={{ marginBottom: '15px', paddingLeft: '10px' }}>
            <p style={{ fontSize: '11px', color: '#8c9eae', marginBottom: '8px' }}>
              Testez la vérification OTP avec les faux dossiers suivants :
            </p>
            {DOSSIERS_DEMO.map((d, idx) => (
              <button
                key={idx}
                className="demo-scenario-btn"
                style={{ width: '100%', padding: '8px', fontSize: '13px', marginBottom: '6px' }}
                onClick={() => runScenario(`dossier-${idx}`, [`Je voudrais suivre le dossier ${d.ref}`], 'public')}
                disabled={playingId !== null}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <strong style={{ color: '#00a884' }}>{d.ref}</strong>
                  <span style={{ fontSize: '11px', color: '#ccc' }}>{d.desc}</span>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* 2. Incitations dynamiques */}
        <SectionHeader id="incit" icon="💰" title="Incitations & Aides" />
        {expandedSection === 'incit' && (
          <div style={{ marginBottom: '15px', paddingLeft: '10px' }}>
            <p style={{ fontSize: '11px', color: '#8c9eae', marginBottom: '8px' }}>
              Déclenche l'arbre interactif basé sur JSON :
            </p>
            <button
               className="demo-scenario-btn" style={{ width: '100%', padding: '10px', fontSize: '13px' }}
               onClick={() => runScenario('incit-1', ['Quelles sont les aides pour les entreprises ?'], 'public')}
               disabled={playingId !== null}
            >
              ▶ Lancer le Workflow
            </button>
          </div>
        )}

        {/* 3. Dashboard Interne */}
        <SectionHeader id="interne" icon="📊" title="Agent Interne" />
        {expandedSection === 'interne' && (
          <div style={{ marginBottom: '15px', paddingLeft: '10px' }}>
            <p style={{ fontSize: '11px', color: '#8c9eae', marginBottom: '8px' }}>
              Base de données et Stats CRI :
            </p>
            <button className="demo-scenario-btn" style={{ width: '100%', padding: '8px', fontSize: '13px', marginBottom: '6px' }}
               onClick={() => runScenario('int-1', ['Tableau de bord complet'], 'internal')} disabled={playingId !== null}>
              📈 Générer Statistiques
            </button>
            <button className="demo-scenario-btn" style={{ width: '100%', padding: '8px', fontSize: '13px', marginBottom: '6px' }}
               onClick={() => runScenario('int-2', ['Montre les dossiers en attente'], 'internal')} disabled={playingId !== null}>
              ⏳ Liste En Attente (Interne)
            </button>
            <button className="demo-scenario-btn" style={{ width: '100%', padding: '8px', fontSize: '13px' }}
               onClick={() => runScenario('int-3', ['Rechercher dossier INV-2024-001'], 'internal')} disabled={playingId !== null}>
              🔍 Recherche sans OTP
            </button>
          </div>
        )}

        {/* 5. Escalade Humaine */}
        <SectionHeader id="esc" icon="🚨" title="Escalade Humaine" />
        {expandedSection === 'esc' && (
          <div style={{ marginBottom: '15px', paddingLeft: '10px' }}>
            <p style={{ fontSize: '11px', color: '#8c9eae', marginBottom: '8px' }}>
               Redirection vers un conseiller :
            </p>
            <button className="demo-scenario-btn" style={{ width: '100%', padding: '10px', fontSize: '13px' }}
               onClick={() => runScenario('escalade', ['Je veux parler à un agent humain s\'il vous plait'], 'public')} disabled={playingId !== null}>
              👨‍💼 Demander un humain
            </button>
          </div>
        )}
      </div>

      <div style={{ marginTop: '15px', borderTop: '1px solid #2d3f50', paddingTop: '15px', flexShrink: 0 }}>
        <button
          className="demo-notify-btn"
          onClick={handleNotify}
          id="demo-notify-btn"
          style={{ width: '100%' }}
        >
          📢 Simuler Notification Push
        </button>
      </div>

    </div>
  );
}
