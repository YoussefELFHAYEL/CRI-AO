import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Edit, Save } from 'lucide-react';
import { API_BASE_URL } from '../../utils/api';

export default function AdminQuestions() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');

  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/admin/questions?status=pending`);
      const data = await res.json();
      setQuestions(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (id, status, newValue = null) => {
    try {
      const payload = { status };
      if (newValue !== null) {
        payload.suggested_answer = newValue;
      }

      const res = await fetch(`${API_BASE_URL}/admin/questions/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        // Remove from list
        setQuestions((prev) => prev.filter((q) => q.id !== id));
        if (editingId === id) setEditingId(null);
      }
    } catch (e) {
      console.error('Error updating question', e);
    }
  };

  const startEdit = (q) => {
    setEditingId(q.id);
    setEditValue(q.suggested_answer || '');
  };

  if (loading) return <div className="admin-view"><p>Chargement des questions...</p></div>;

  return (
    <div className="admin-view">
      <h1 style={{ marginBottom: '20px', color: '#1e1e2d' }}>Questions Non Reconnues</h1>
      <p style={{ color: '#b5b5c3', marginBottom: '30px' }}>
        Validez ou rejetez les réponses aux questions que le chatbot n'a pas su traiter avec confiance.
      </p>

      {questions.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', background: '#f9f9f9', borderRadius: '8px' }}>
          <CheckCircle size={48} color="#00a884" style={{ marginBottom: '10px' }} />
          <h3>Super ! Vous êtes à jour.</h3>
          <p style={{ color: '#888' }}>Aucune nouvelle question en attente.</p>
        </div>
      ) : (
        <div className="questions-list" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {questions.map((q) => (
            <div key={q.id} className="question-card" style={{ border: '1px solid #e4e6ef', borderRadius: '8px', padding: '20px', background: 'white', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <h4 style={{ margin: '0 0 10px 0', color: '#1e1e2d' }}>Utilisateur : "{q.question}"</h4>
                  <span style={{ fontSize: '12px', color: '#b5b5c3' }}>Parvenu le {new Date(q.created_at).toLocaleString()}</span>
                </div>
              </div>

              {editingId === q.id ? (
                <div style={{ background: '#f3f4f6', padding: '15px', borderRadius: '8px' }}>
                  <label style={{ display: 'block', marginBottom: '10px', fontWeight: '500', fontSize: '14px' }}>Réponse suggérée (Édition) :</label>
                  <textarea
                    style={{ width: '100%', height: '100px', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box' }}
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                  />
                  <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
                    <button onClick={() => handleUpdate(q.id, 'validated', editValue)} style={{ background: '#00a884', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Save size={16} /> Sauvegarder et Valider
                    </button>
                    <button onClick={() => setEditingId(null)} style={{ background: '#bbb', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer' }}>Annuler</button>
                  </div>
                </div>
              ) : (
                <div style={{ background: '#f3f4f6', padding: '15px', borderRadius: '8px' }}>
                  <p style={{ margin: 0, color: '#3f4254', whiteSpace: 'pre-line' }}>{q.suggested_answer || "Aucune suggestion trouvée."}</p>
                </div>
              )}

              {editingId !== q.id && (
                <div style={{ display: 'flex', gap: '10px', marginTop: '5px' }}>
                  <button onClick={() => handleUpdate(q.id, 'validated')} style={{ background: 'rgba(0, 168, 132, 0.1)', color: '#00a884', padding: '8px 16px', borderRadius: '6px', border: '1px solid #00a884', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '500' }}>
                    <CheckCircle size={16} /> Valider
                  </button>
                  <button onClick={() => startEdit(q)} style={{ background: 'rgba(0, 0, 0, 0.05)', color: '#555', padding: '8px 16px', borderRadius: '6px', border: '1px solid #ccc', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '500' }}>
                    <Edit size={16} /> Modifier
                  </button>
                  <button onClick={() => handleUpdate(q.id, 'rejected')} style={{ background: 'rgba(255, 0, 0, 0.05)', color: '#d9534f', padding: '8px 16px', borderRadius: '6px', border: '1px solid #d9534f', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '500' }}>
                    <XCircle size={16} /> Rejeter
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
