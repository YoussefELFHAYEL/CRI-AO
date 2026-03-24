import React, { useState, useEffect } from 'react';
import { faker } from '@faker-js/faker';

export default function AdminContacts() {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const itemsPerPage = 20;

  useEffect(() => {
    // Generate 100 fake contacts to simulate a subset of the 20,000 spec
    const generateContacts = () => {
      const arr = [];
      for (let i = 0; i < 100; i++) {
        arr.push({
          id: faker.string.uuid(),
          name: faker.person.fullName(),
          phone: `+212 6 ${faker.string.numeric(2)} ${faker.string.numeric(2)} ${faker.string.numeric(2)} ${faker.string.numeric(2)}`,
          email: faker.internet.email(),
          company: faker.company.name(),
          source: i % 3 === 0 ? 'Site Web' : i % 2 === 0 ? 'WhatsApp' : 'Formulaire CRI',
        });
      }
      return arr;
    };

    setContacts(generateContacts());
    setLoading(false);
  }, []);

  const totalPages = Math.ceil(contacts.length / itemsPerPage);
  const displayContacts = contacts.slice((page - 1) * itemsPerPage, page * itemsPerPage);

  if (loading) return <div className="admin-view">Chargement des 20 000 contacts...</div>;

  return (
    <div className="admin-view">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0, color: '#1e1e2d' }}>Liste des Contacts <span style={{ fontSize: '14px', color: '#b5b5c3', fontWeight: 'normal' }}>(Mocked: 102 / 20,000)</span></h1>
      </div>

      <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e4e6ef', color: '#b5b5c3' }}>
              <th style={{ padding: '12px' }}>Nom complet</th>
              <th style={{ padding: '12px' }}>Téléphone</th>
              <th style={{ padding: '12px' }}>Email</th>
              <th style={{ padding: '12px' }}>Entreprise</th>
              <th style={{ padding: '12px' }}>Source</th>
            </tr>
          </thead>
          <tbody>
            {displayContacts.map(c => (
              <tr key={c.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px', fontWeight: '500', color: '#1e1e2d' }}>{c.name}</td>
                <td style={{ padding: '12px', color: '#00a884', fontFamily: 'monospace', fontSize: '14px' }}>{c.phone}</td>
                <td style={{ padding: '12px', color: '#555', fontSize: '14px' }}>{c.email}</td>
                <td style={{ padding: '12px', color: '#555' }}>{c.company}</td>
                <td style={{ padding: '12px' }}>
                  <span style={{ background: '#f8f9fa', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>{c.source}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '10px' }}>
        <button 
          onClick={() => setPage(p => Math.max(1, p - 1))} 
          disabled={page === 1}
          style={{ padding: '8px 16px', background: page === 1 ? '#f3f4f6' : '#e4e6ef', border: 'none', borderRadius: '6px', cursor: page === 1 ? 'not-allowed' : 'pointer' }}
        >
          Précédent
        </button>
        <span style={{ padding: '8px 16px' }}>Page {page} / {totalPages}</span>
        <button 
          onClick={() => setPage(p => Math.min(totalPages, p + 1))} 
          disabled={page === totalPages}
          style={{ padding: '8px 16px', background: page === totalPages ? '#f3f4f6' : '#e4e6ef', border: 'none', borderRadius: '6px', cursor: page === totalPages ? 'not-allowed' : 'pointer' }}
        >
          Suivant
        </button>
      </div>
    </div>
  );
}
