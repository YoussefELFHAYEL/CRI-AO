import React, { useState } from 'react';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, MessageSquareWarning, FileText, Users, BarChart, FolderKanban, LogOut, MessageCircle, Contact } from 'lucide-react';
import './admin.css';

import AdminHome from '../components/admin/AdminHome.jsx';
import AdminQuestions from '../components/admin/AdminQuestions.jsx';

import AdminMessages from '../components/admin/AdminMessages.jsx';
import AdminDossiers from '../components/admin/AdminDossiers.jsx';
import AdminContacts from '../components/admin/AdminContacts.jsx';

import AdminKnowledge from '../components/admin/AdminKnowledge.jsx';
import AdminAdmins from '../components/admin/AdminAdmins.jsx';
import AdminCampaigns from '../components/admin/AdminCampaigns.jsx';

export default function AdminDashboard() {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  // Fake auth
  const isAuthenticated = localStorage.getItem('adminToken') !== null;

  if (!isAuthenticated) {
    return (
      <div className="admin-login-container">
        <form className="admin-login-form" onSubmit={(e) => {
          e.preventDefault();
          localStorage.setItem('adminToken', 'mock-jwt-token');
          window.location.reload();
        }}>
          <div style={{ textAlign: 'center', marginBottom: '20px', fontSize: '40px' }}>🇲🇦</div>
          <h2>CRI-RSK Administrateur</h2>
          <div className="form-group">
            <input type="email" placeholder="Email" defaultValue="demo@cri-rsk.ma" required />
          </div>
          <div className="form-group">
            <input type="password" placeholder="Mot de passe" defaultValue="admin123" required />
          </div>
          <button type="submit" className="admin-btn-primary">Se connecter</button>
        </form>
      </div>
    );
  }

  const navItems = [
    { path: '', label: 'Vue d\'ensemble', icon: <LayoutDashboard size={20}/> },
    { path: 'questions', label: 'Questions non reconnues', icon: <MessageSquareWarning size={20}/> },
    { path: 'knowledge', label: 'Base de données', icon: <FileText size={20}/> },
    { path: 'admins', label: 'Gestion Admins', icon: <Users size={20}/> },
    { path: 'messages', label: 'Stats Messages', icon: <BarChart size={20}/> },
    { path: 'dossiers', label: 'Suivi Dossiers', icon: <FolderKanban size={20}/> },
    { path: 'contacts', label: 'Contacts (20k)', icon: <Contact size={20}/> },
    { path: 'campaigns', label: 'Publipostage', icon: <MessageCircle size={20}/> },
  ];

  return (
    <div className="admin-layout">
      <aside className={`admin-sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
        <div className="admin-sidebar-header">
          <h2>CRI <span>Admin</span></h2>
        </div>
        <nav className="admin-nav">
          {navItems.map(item => {
            // Determine active exact or starts_with
            const isActive = item.path === '' 
              ? location.pathname === '/admin' || location.pathname === '/admin/'
              : location.pathname.startsWith(`/admin/${item.path}`);
              
            return (
              <Link 
                to={`/admin/${item.path}`} 
                key={item.path}
                className={`admin-nav-item ${isActive ? 'active' : ''}`}
              >
                {item.icon}
                <span className="nav-label">{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="admin-sidebar-footer">
          <button className="admin-logout-btn" onClick={() => {
            localStorage.removeItem('adminToken');
            window.location.reload();
          }}>
            <LogOut size={20} />
            <span className="nav-label">Déconnexion</span>
          </button>
        </div>
      </aside>

      <main className="admin-content">
        <header className="admin-topbar">
          <button className="hamburger-btn" onClick={() => setSidebarOpen(!isSidebarOpen)}>☰</button>
          <div className="admin-topbar-profile">
            <span className="admin-avatar">A</span>
            <span className="admin-name">Admin Démo</span>
          </div>
        </header>

        <div className="admin-main-area">
          <Routes>
            <Route path="/" element={<AdminHome />} />
            <Route path="questions" element={<AdminQuestions />} />
            <Route path="knowledge" element={<AdminKnowledge />} />
            <Route path="admins" element={<AdminAdmins />} />
            <Route path="messages" element={<AdminMessages />} />
            <Route path="dossiers" element={<AdminDossiers />} />
            <Route path="contacts" element={<AdminContacts />} />
            <Route path="campaigns" element={<AdminCampaigns />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
