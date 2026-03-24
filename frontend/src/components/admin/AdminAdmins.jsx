import React, { useState } from 'react';
import { UserPlus, PowerOff } from 'lucide-react';

export default function AdminAdmins() {
  const [admins, setAdmins] = useState([
    { id: 1, name: 'Admin Principal', email: 'demo@cri-rsk.ma', phone: '+212 600 000 000', entity: 'Direction Générale', role: 'Super Admin', active: true },
    { id: 2, name: 'Agent Support', email: 'support@cri-rsk.ma', phone: '+212 600 111 222', entity: 'Pôle Impulsion', role: 'Conseiller', active: true },
    { id: 3, name: 'Consultant', email: 'consultant@cri-rsk.ma', phone: '+212 600 333 444', entity: 'Guichet Unique', role: 'Lecteur', active: false },
  ]);

  const [showModal, setShowModal] = useState(false);

  const toggleStatus = (id) => {
    setAdmins(admins.map(a => a.id === id ? { ...a, active: !a.active } : a));
  };

  const handleAdd = (e) => {
    e.preventDefault();
    if (admins.length >= 10) return alert('Limite de 10 administrateurs atteinte.');
    const formData = new FormData(e.target);
    const newAdmin = {
      id: Date.now(),
      name: formData.get('name'),
      email: formData.get('email'),
      phone: formData.get('phone'),
      entity: formData.get('entity'),
      role: formData.get('role'),
      active: true,
    };
    setAdmins([...admins, newAdmin]);
    setShowModal(false);
  };

  return (
    <div className="admin-view">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{ margin: 0, color: '#1e1e2d' }}>Gestion des Administrateurs</h1>
          <p style={{ color: '#b5b5c3', margin: '5px 0 0 0' }}>Compteur: {admins.length}/10</p>
        </div>
        <button 
          onClick={() => setShowModal(true)} 
          disabled={admins.length >= 10}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', background: '#00a884', color: 'white', border: 'none', borderRadius: '6px', cursor: admins.length >= 10 ? 'not-allowed' : 'pointer', fontWeight: '500' }}
        >
          <UserPlus size={16} /> Ajouter un admin
        </button>
      </div>

      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #e4e6ef', color: '#b5b5c3' }}>
            <th style={{ padding: '12px' }}>Nom</th>
            <th style={{ padding: '12px' }}>Email</th>
            <th style={{ padding: '12px' }}>Téléphone</th>
            <th style={{ padding: '12px' }}>Entité</th>
            <th style={{ padding: '12px' }}>Rôle</th>
            <th style={{ padding: '12px' }}>Statut</th>
            <th style={{ padding: '12px' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {admins.map(a => (
            <tr key={a.id} style={{ borderBottom: '1px solid #f3f4f6', opacity: a.active ? 1 : 0.6 }}>
              <td style={{ padding: '12px', fontWeight: '500' }}>{a.name}</td>
              <td style={{ padding: '12px', color: '#555' }}>{a.email}</td>
              <td style={{ padding: '12px', color: '#555' }}>{a.phone}</td>
              <td style={{ padding: '12px', color: '#555' }}>{a.entity}</td>
              <td style={{ padding: '12px', color: '#555' }}>{a.role}</td>
              <td style={{ padding: '12px' }}>
                <span style={{ padding: '4px 8px', borderRadius: '4px', fontSize: '12px', background: a.active ? '#d4edda' : '#f8d7da', color: a.active ? '#155724' : '#721c24' }}>
                  {a.active ? 'Actif' : 'Inactif'}
                </span>
              </td>
              <td style={{ padding: '12px' }}>
                <button onClick={() => toggleStatus(a.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: a.active ? '#dc3545' : '#28a745' }} title={a.active ? "Désactiver" : "Activer"}>
                  <PowerOff size={18} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <form onSubmit={handleAdd} style={{ background: 'white', padding: '30px', borderRadius: '12px', width: '400px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <h3 style={{ margin: '0 0 10px 0' }}>Ajouter un admin</h3>
            <input name="name" placeholder="Nom complet" required style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc' }} />
            <input name="email" type="email" placeholder="Email" required style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc' }} />
            <input name="phone" placeholder="Téléphone" required style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc' }} />
            <input name="entity" placeholder="Entité" required style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc' }} />
            <select name="role" style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ccc' }}>
              <option value="Conseiller">Conseiller</option>
              <option value="Super Admin">Super Admin</option>
              <option value="Lecteur">Lecteur</option>
            </select>
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
              <button type="submit" style={{ flex: 1, padding: '10px', background: '#00a884', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>Enregistrer</button>
              <button type="button" onClick={() => setShowModal(false)} style={{ flex: 1, padding: '10px', background: '#e4e6ef', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>Annuler</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
