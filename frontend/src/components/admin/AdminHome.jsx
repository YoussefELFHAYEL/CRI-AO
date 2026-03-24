import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../../utils/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function AdminHome() {
  const [stats, setStats] = useState({ total_messages: 0, resolution_rate: '0%', avg_rating: '0', total_dossiers: 0 });

  useEffect(() => {
    fetch(`${API_BASE_URL}/admin/stats`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(e => console.error(e));
  }, []);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Conversations par heure (Simulation)' },
    },
  };

  const chartData = {
    labels: ['08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h'],
    datasets: [
      {
        label: 'Conversations reçues',
        data: [12, 19, 45, 60, 20, 30, 80, 50, 24],
        backgroundColor: '#00a884',
      },
    ],
  };

  return (
    <div className="admin-view" style={{ background: 'transparent', padding: '0', boxShadow: 'none' }}>
      <h1 style={{ marginBottom: '20px', color: '#1e1e2d' }}>Vue d'ensemble</h1>
      
      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div style={{ background: 'white', padding: '20px', borderRadius: '12px', borderLeft: '4px solid #00a884', boxShadow: '0 5px 15px rgba(0,0,0,0.03)' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#888', fontWeight: '500' }}>Messages Reçus</h4>
          <span style={{ fontSize: '32px', fontWeight: 'bold', color: '#1e1e2d' }}>{stats.total_messages}</span>
        </div>
        <div style={{ background: 'white', padding: '20px', borderRadius: '12px', borderLeft: '4px solid #00a884', boxShadow: '0 5px 15px rgba(0,0,0,0.03)' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#888', fontWeight: '500' }}>Taux de Résolution</h4>
          <span style={{ fontSize: '32px', fontWeight: 'bold', color: '#00a884' }}>{stats.resolution_rate}</span>
        </div>
        <div style={{ background: 'white', padding: '20px', borderRadius: '12px', borderLeft: '4px solid #00a884', boxShadow: '0 5px 15px rgba(0,0,0,0.03)' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#888', fontWeight: '500' }}>Note Moyenne</h4>
          <span style={{ fontSize: '32px', fontWeight: 'bold', color: '#f39c12' }}>⭐ {stats.avg_rating}</span>
        </div>
        <div style={{ background: 'white', padding: '20px', borderRadius: '12px', borderLeft: '4px solid #00a884', boxShadow: '0 5px 15px rgba(0,0,0,0.03)' }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#888', fontWeight: '500' }}>Dossiers Suivis</h4>
          <span style={{ fontSize: '32px', fontWeight: 'bold', color: '#1e1e2d' }}>{stats.total_dossiers}</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px' }}>
        {/* Chart */}
        <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 5px 15px rgba(0,0,0,0.03)' }}>
          <Bar options={chartOptions} data={chartData} />
        </div>

        {/* Top 5 list */}
        <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 5px 15px rgba(0,0,0,0.03)' }}>
          <h3 style={{ margin: '0 0 20px 0', color: '#1e1e2d', fontSize: '16px' }}>Top 5 requêtes fréquents</h3>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {['1. Suivi d\'un dossier d\'investissement', '2. Demande des incitations PME', '3. Création de société (SARL)', '4. Aides secteur Agricole', '5. Parler avec un agent'].map(q => (
              <li key={q} style={{ padding: '10px', background: '#f8f9fa', borderRadius: '6px', fontSize: '14px', color: '#333' }}>
                {q}
              </li>
            ))}
          </ul>
        </div>
      </div>

    </div>
  );
}
