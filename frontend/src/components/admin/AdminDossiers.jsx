import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../utils/api';
import { BellRing, FileSignature } from 'lucide-react';

export default function AdminDossiers() {
  const [dossiers, setDossiers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/admin/dossiers`)
      .then(res => res.json())
      .then(data => setDossiers(data))
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  const handleStatusChange = async (id, newStatus) => {
    try {
      const res = await fetch(`${API_BASE_URL}/admin/dossiers/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        setDossiers(prev => prev.map(d => d.id === id ? { ...d, status: newStatus } : d));
        // Mocking the push notification UI effect
        alert("📢 Notification Push simulée envoyée à l'usager sur WhatsApp :\n\n'Votre dossier d\'investissement a changé de statut.'");
      }
    } catch (e) {
      console.error(e);
    }
  };

  const getStatusColor = (status) => {
    if (status.includes('Validé')) return '#28a745';
    if (status.includes('Rejeté')) return '#dc3545';
    if (status.includes('attente')) return '#f39c12';
    return '#17a2b8';
  };

  if (loading) return <div className="admin-view">Chargement...</div>;

  return (
    <div className="admin-view">
      <h1 style={{ marginBottom: '20px', color: '#1e1e2d' }}>Suivi des Dossiers</h1>
      <p style={{ color: '#888', marginBottom: '30px' }}>Modifiez le statut d'un dossier pour déclencher automatiquement une alerte WhatsApp.</p>

      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #e4e6ef', color: '#b5b5c3' }}>
            <th style={{ padding: '12px' }}>Référence</th>
            <th style={{ padding: '12px' }}>Entreprise</th>
            <th style={{ padding: '12px' }}>Type de Projet</th>
            <th style={{ padding: '12px' }}>Statut Actuel</th>
            <th style={{ padding: '12px' }}>Actions Rapides</th>
          </tr>
        </thead>
        <tbody>
          {dossiers.map(d => (
            <tr key={d.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
              <td style={{ padding: '12px', fontWeight: 'bold' }}>{d.reference}</td>
              <td style={{ padding: '12px', color: '#555' }}>{d.company_name}</td>
              <td style={{ padding: '12px', color: '#555' }}>{d.project_type}</td>
              <td style={{ padding: '12px' }}>
                <span style={{ 
                  color: getStatusColor(d.status), 
                  padding: '4px 8px', 
                  borderRadius: '12px', 
                  border: `1px solid ${getStatusColor(d.status)}`,
                  fontSize: '12px', 
                  fontWeight: '600'
                }}>
                  {d.status}
                </span>
              </td>
              <td style={{ padding: '12px' }}>
                <select 
                  style={{ padding: '6px', borderRadius: '4px', border: '1px solid #ccc', marginRight: '10px' }}
                  onChange={(e) => {
                    if (e.target.value !== d.status) {
                      handleStatusChange(d.id, e.target.value);
                    }
                  }}
                  value={d.status}
                >
                  <option value="En cours d'examen">En cours d'examen</option>
                  <option value="Validé par la commission">Validé par la commission</option>
                  <option value="En attente de documents">En attente de documents</option>
                  <option value="Rejeté">Rejeté</option>
                </select>
                <button 
                  onClick={() => alert(`Rappel envoyé à l'entreprise ${d.company_name}`)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#00a884' }}
                  title="Envoyer un rappel"
                >
                  <BellRing size={18} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
