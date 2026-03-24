import React, { useState } from 'react';
import { BookOpen, ToggleLeft, ToggleRight, PlusCircle } from 'lucide-react';

export default function AdminKnowledge() {
  const [documents, setDocuments] = useState([
    { id: 1, title: '_all_incitations.json', type: 'JSON Structuré', blocked: false },
    { id: 2, title: 'PROCEDURE_CREATION_SARL.txt', type: 'Texte Brut', blocked: false },
    { id: 3, title: 'LOI_INVESTISSEMENT_AGR.pdf', type: 'Document Royal', blocked: true },
    { id: 4, title: 'Q&A Custom (Manuelle)', type: 'Manuel', blocked: false },
  ]);

  const [showAdd, setShowAdd] = useState(false);

  const toggleBlock = (id) => {
    setDocuments(documents.map(d => d.id === id ? { ...d, blocked: !d.blocked } : d));
  };

  const handleAdd = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const newDoc = {
      id: Date.now(),
      title: formData.get('question').substring(0, 30) + '...',
      type: 'Q&R Manuel',
      blocked: false,
    };
    setDocuments([newDoc, ...documents]);
    setShowAdd(false);
  };

  return (
    <div className="admin-view">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{ margin: 0, color: '#1e1e2d' }}>Base de Connaissances</h1>
          <p style={{ color: '#b5b5c3', margin: '5px 0 0 0' }}>{documents.length} sources dans ChromaDB</p>
        </div>
        <button 
          onClick={() => setShowAdd(true)} 
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', background: '#00a884', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' }}
        >
          <PlusCircle size={16} /> Ajouter Q&R
        </button>
      </div>

      {showAdd && (
        <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #e4e6ef' }}>
          <h3 style={{ marginTop: 0 }}>Ajout manuel dans ChromaDB</h3>
          <form onSubmit={handleAdd} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <input name="question" placeholder="Question typique..." required style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc' }} />
            <textarea name="answer" placeholder="Réponse exacte à forcer..." required style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc', minHeight: '80px' }} />
            <div style={{ display: 'flex', gap: '10px' }}>
              <button type="submit" style={{ padding: '10px 20px', background: '#00a884', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>Forcer Ingestion Vectorielle</button>
              <button type="button" onClick={() => setShowAdd(false)} style={{ padding: '10px 20px', background: '#e4e6ef', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>Fermer</button>
            </div>
          </form>
        </div>
      )}

      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #e4e6ef', color: '#b5b5c3' }}>
            <th style={{ padding: '12px' }}><BookOpen size={16} /> Nom du document</th>
            <th style={{ padding: '12px' }}>Type</th>
            <th style={{ padding: '12px' }}>Statut</th>
            <th style={{ padding: '12px' }}>Action RAG</th>
          </tr>
        </thead>
        <tbody>
          {documents.map(d => (
            <tr key={d.id} style={{ borderBottom: '1px solid #f3f4f6', opacity: d.blocked ? 0.6 : 1 }}>
              <td style={{ padding: '12px', fontWeight: '500' }}>{d.title}</td>
              <td style={{ padding: '12px', color: '#555' }}>
                <span style={{ fontSize: '12px', padding: '4px 8px', background: '#e4e6ef', borderRadius: '4px' }}>{d.type}</span>
              </td>
              <td style={{ padding: '12px' }}>
                <span style={{ fontSize: '12px', fontWeight: 'bold', color: d.blocked ? '#dc3545' : '#28a745' }}>
                  {d.blocked ? 'Bloqué (Ignoré)' : 'Actif (Indéxé)'}
                </span>
              </td>
              <td style={{ padding: '12px' }}>
                <button onClick={() => toggleBlock(d.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: d.blocked ? '#dc3545' : '#00a884' }} title="Toggle">
                  {d.blocked ? <ToggleLeft size={24} /> : <ToggleRight size={24} />}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
