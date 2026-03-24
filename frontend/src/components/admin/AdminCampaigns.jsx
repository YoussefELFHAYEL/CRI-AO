import React, { useState } from 'react';
import { FileUp, Send, CheckCircle2, AlertCircle } from 'lucide-react';
import Papa from 'papaparse';

const TEMPLATES = [
  {
    id: 1,
    name: 'Rappel dossier',
    content: 'Bonjour {name}, votre dossier {reference} attend une action de votre part sur le portail CRI-RSK. Merci de vous connecter pour finaliser la procédure.'
  },
  {
    id: 2,
    name: 'Confirmation',
    content: 'Bonjour {name}, nous avons le plaisir de vous informer que votre dossier {reference} a été validé. Vous recevrez l\'agrément prochainement.'
  },
  {
    id: 3,
    name: 'Invitation événement',
    content: 'Bonjour {name}, le CRI-RSK vous invite à la journée de l\'Investisseur le 15 Avril à Rabat. Confirmez votre présence !'
  }
];

export default function AdminCampaigns() {
  const [csvData, setCsvData] = useState([]);
  const [templateId, setTemplateId] = useState(1);
  const [status, setStatus] = useState('idle'); // idle, sending, complete
  const [results, setResults] = useState({ success: 0, failed: 0 });

  const activeTemplate = TEMPLATES.find(t => t.id === templateId);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (result) => {
        setCsvData(result.data);
      }
    });
  };

  const getPreview = () => {
    if (csvData.length === 0) return 'Veuillez charger un fichier CSV contenant les colonnes {name} et {reference}.';
    const sample = csvData[0];
    let preview = activeTemplate.content;
    preview = preview.replace(/{name}/g, sample.name || '[Nom]');
    preview = preview.replace(/{reference}/g, sample.reference || '[REF]');
    return preview;
  };

  const handleSend = () => {
    if (csvData.length === 0) return alert('Aucun destinataire chargé.');
    setStatus('sending');
    
    // Simulate sending progress
    setTimeout(() => {
      setStatus('complete');
      // 95% success rate simulation
      const successCount = Math.floor(csvData.length * 0.95);
      setResults({
        success: successCount,
        failed: csvData.length - successCount
      });
    }, 2500);
  };

  return (
    <div className="admin-view">
      <h1 style={{ marginBottom: '10px', color: '#1e1e2d' }}>Publipostage (Bulk Messaging WhatsApp)</h1>
      <p style={{ color: '#b5b5c3', marginBottom: '30px' }}>Diffusez des messages de masse à vos investisseurs via l'API WhatsApp Business.</p>

      {status === 'complete' ? (
        <div style={{ background: '#f8f9fa', padding: '40px', borderRadius: '12px', textAlign: 'center', border: '1px solid #e4e6ef' }}>
          <CheckCircle2 size={64} color="#00a884" style={{ marginBottom: '20px' }} />
          <h2 style={{ margin: '0 0 10px 0' }}>Campagne terminée avec succès</h2>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '40px', marginTop: '20px' }}>
            <div style={{ textAlign: 'center' }}>
              <span style={{ fontSize: '32px', fontWeight: 'bold', color: '#00a884' }}>{results.success}</span>
              <p style={{ margin: 0, color: '#888' }}>Messages Délivrés</p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <span style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc3545' }}>{results.failed}</span>
              <p style={{ margin: 0, color: '#888' }}>Échecs</p>
            </div>
          </div>
          <button onClick={() => { setStatus('idle'); setCsvData([]); }} style={{ marginTop: '30px', padding: '10px 24px', background: '#e4e6ef', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' }}>
            Nouvelle campagne
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '30px', flexDirection: 'column' }}>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
            {/* Left Col: Setup */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              
              <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', border: '1px dashed #ccc' }}>
                <h3 style={{ margin: '0 0 15px 0' }}>1. Charger les Cibles (CSV)</h3>
                <label style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '30px', border: '2px dashed #00a884', borderRadius: '8px', cursor: 'pointer', background: 'rgba(0,168,132,0.05)' }}>
                  <FileUp size={32} color="#00a884" style={{ marginBottom: '10px' }} />
                  <span style={{ color: '#00a884', fontWeight: '500' }}>Parcourir ou glisser un fichier CSV</span>
                  <input type="file" accept=".csv" onChange={handleFileUpload} style={{ display: 'none' }} />
                </label>
                {csvData.length > 0 && (
                  <p style={{ margin: '15px 0 0 0', color: '#28a745', fontWeight: '500' }}>✅ {csvData.length} destinataires détectés.</p>
                )}
              </div>

              <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', border: '1px solid #e4e6ef' }}>
                <h3 style={{ margin: '0 0 15px 0' }}>2. Modèle de Message</h3>
                <select 
                  value={templateId} 
                  onChange={(e) => setTemplateId(Number(e.target.value))}
                  style={{ width: '100%', padding: '12px', borderRadius: '6px', border: '1px solid #ccc', fontSize: '15px' }}
                >
                  {TEMPLATES.map(t => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>

            </div>

            {/* Right Col: Preview */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              
              <div style={{ background: '#e5ddd5', padding: '20px', borderRadius: '8px', border: '1px solid #d1d7db', flex: 1, display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ margin: '0 0 15px 0', color: '#1e1e2d' }}>3. Aperçu Rendu WhatsApp</h3>
                <div style={{ background: '#d9fdd3', padding: '15px', borderRadius: '8px', borderBottomRightRadius: 0, boxShadow: '0 1px 2px rgba(0,0,0,0.1)', alignSelf: 'flex-end', maxWidth: '80%' }}>
                  <p style={{ margin: 0, color: '#111b21', whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
                    {getPreview()}
                  </p>
                  <div style={{ textAlign: 'right', fontSize: '11px', color: '#667781', marginTop: '5px' }}>14:30 ✓✓</div>
                </div>
              </div>

            </div>
          </div>

          <div style={{ borderTop: '2px solid #e4e6ef', paddingTop: '20px' }}>
            <button 
              onClick={handleSend} 
              disabled={csvData.length === 0 || status === 'sending'}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', width: '100%', padding: '16px', background: csvData.length === 0 ? '#ccc' : '#00a884', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: '600', cursor: csvData.length === 0 ? 'not-allowed' : 'pointer', opacity: status === 'sending' ? 0.7 : 1 }}
            >
              {status === 'sending' ? (
                <><AlertCircle className="spin" size={20} /> Envoi en cours...</>
              ) : (
                <><Send size={20} /> Diffuser la campagne à {csvData.length || 0} destinataires</>
              )}
            </button>
          </div>

        </div>
      )}
    </div>
  );
}
