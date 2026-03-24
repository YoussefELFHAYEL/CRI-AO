import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageCircle, ShieldCheck, Zap, BrainCircuit, Users, Building2, BarChart3, Database } from 'lucide-react';
import './LandingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      {/* Navbar Optionnelle */}
      <nav className="landing-nav">
        <div className="logo-area">
          <span className="logo-icon">🇲🇦</span>
          <span className="logo-text">CRI-RSK Chatbot</span>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            L'Intelligence Artificielle au service de <br/>
            <span className="text-gradient">l'Investissement Régional</span>
          </h1>
          <p className="hero-subtitle">
            Une solution WhatsApp IA Trilingue (FR, AR, EN) capable d'orienter les investisseurs 
            et de fournir un suivi de dossier en temps réel pour le CRI Rabat-Salé-Kénitra.
          </p>
          
          <div className="hero-buttons">
            <button className="btn-primary" onClick={() => navigate('/chat')}>
              <MessageCircle size={20} />
              Tester Agent Public WhatsApp
            </button>
            <button className="btn-secondary" onClick={() => navigate('/admin')}>
              <ShieldCheck size={20} />
              Accès Dashboard Admin
            </button>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="hero-blob blob-1"></div>
        <div className="hero-blob blob-2"></div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <h2 className="section-title">Découvrez les fonctionnalités</h2>
        <div className="features-grid">
          
          <div className="feature-card">
            <div className="feature-icon"><BrainCircuit size={28} /></div>
            <h3>RAG Multilingue</h3>
            <p>Le bot comprend et répond nativement en Français, Arabe et Anglais grâce à un modèle sémantique avancé.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon"><Building2 size={28} /></div>
            <h3>Incitations dynamiques</h3>
            <p>Arbre de décision interactif guidant l'usager vers les subventions de l'État adaptées à son profil.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon"><Zap size={28} /></div>
            <h3>Suivi Dossier OTP</h3>
            <p>Sécurisation du suivi de dossier d'investissement avec génération d'OTP dynamique sans quitter WhatsApp.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon"><BarChart3 size={28} /></div>
            <h3>Dashboard Interne</h3>
            <p>Outils d'analyse, KPIs de performance et publipostage dédié aux administrateurs du CRI.</p>
          </div>

        </div>
      </section>

      {/* Tech Stack */}
      <section className="tech-section">
        <h2 className="section-title">Architecture & Technologies</h2>
        <div className="tech-logos">
          <div className="tech-item"><Database size={40} /><span>PostgreSQL & pgvector</span></div>
          <div className="tech-item"><span style={{fontSize: '40px'}}>🐍</span><span>FastAPI & Python</span></div>
          <div className="tech-item"><span style={{fontSize: '40px'}}>⚛️</span><span>React & Vite</span></div>
          <div className="tech-item"><span style={{fontSize: '40px'}}>🧠</span><span>OpenAI & HuggingFace</span></div>
          <div className="tech-item"><span style={{fontSize: '40px'}}>⚡</span><span>Redis & Upstash</span></div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <p>© 2026 CRI Rabat-Salé-Kénitra - Prototype IA pour Appel d'Offres</p>
      </footer>
    </div>
  );
}
