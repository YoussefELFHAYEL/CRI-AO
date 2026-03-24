import React, { useState, useEffect } from 'react';
import { Download, Search } from 'lucide-react';
import { API_BASE_URL } from '../../utils/api';

export default function AdminMessages() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetch(`${API_BASE_URL}/admin/messages`)
      .then(r => r.json())
      .then(data => setMessages(data))
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  const handleExport = () => {
    // Simple CSV Export logic
    const headers = ['Date', 'Role', 'Contenu', 'Langue'];
    const rows = messages.map(m => [
      new Date(m.created_at).toLocaleString(),
      m.role,
      `"${m.content.replace(/"/g, '""')}"`,
      m.language || 'N/A'
    ]);
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'messages_export.csv';
    a.click();
  };

  const filtered = messages.filter(m => m.content.toLowerCase().includes(filter.toLowerCase()));

  if (loading) return <div className="admin-view">Chargement...</div>;

  return (
    <div className="admin-view">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0, color: '#1e1e2d' }}>Historique des Messages</h1>
        <button onClick={handleExport} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', background: '#e4e6ef', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' }}>
          <Download size={16} /> Exporter CSV
        </button>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', background: '#f3f4f6', padding: '10px', borderRadius: '8px', marginBottom: '20px' }}>
        <Search size={18} color="#888" style={{ marginRight: '10px' }} />
        <input 
          type="text" 
          placeholder="Rechercher dans les messages..." 
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ border: 'none', background: 'transparent', outline: 'none', width: '100%', fontSize: '15px' }} 
        />
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e4e6ef', color: '#b5b5c3' }}>
              <th style={{ padding: '12px' }}>Date</th>
              <th style={{ padding: '12px' }}>Rôle</th>
              <th style={{ padding: '12px' }}>Langue</th>
              <th style={{ padding: '12px' }}>Contenu</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(m => (
              <tr key={m.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px', fontSize: '14px', color: '#888' }}>{new Date(m.created_at).toLocaleString()}</td>
                <td style={{ padding: '12px' }}>
                  <span style={{ 
                    padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold',
                    background: m.role === 'bot' ? 'rgba(0,168,132,0.1)' : '#f3f4f6',
                    color: m.role === 'bot' ? '#00a884' : '#555'
                  }}>
                    {m.role === 'bot' ? 'Assistant IA' : 'Utilisateur'}
                  </span>
                </td>
                <td style={{ padding: '12px', fontSize: '14px' }}>{m.language?.toUpperCase() || '-'}</td>
                <td style={{ padding: '12px', fontSize: '14px', maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {m.content}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan="4" style={{ textAlign: 'center', padding: '20px', color: '#888' }}>Aucun message trouvé.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
