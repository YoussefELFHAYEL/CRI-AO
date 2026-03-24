# 🚀 Guide de Démonstration - CRI-RSK Chatbot & Admin Dashboard

Ce document contient le script étape par étape pour réaliser une démonstration fluide et impressionnante du projet **CRI-RSK Chatbot** face au jury.

---

## 🛠️ 1. Préparation avant la Démo

Avant de partager votre écran ou de débuter l'appel avec le jury, vérifiez que votre environnement tourne correctement :

1. **Lancer le Backend (Terminal 1) :**
   ```bash
   cd backend
   .\venv\Scripts\activate
   uvicorn app.main:app --reload
   ```
2. **Lancer le Frontend (Terminal 2) :**
   ```bash
   cd frontend
   npm run dev
   ```
3 **Ouvrir les onglets du navigateur :**
   - Onglet 1 : `http://localhost:5173/` (Landing Page Publique)
   - Onglet 2 : `http://localhost:5173/admin` (Dashboard Admin - Connectez-vous avec `demo@cri-rsk.ma` / `admin123` et gardez-le prêt).

---

## 🎥 2. Le Script de la Dématérialisation (Scénarios)

### 🌟 Scénario 1 : Le Portail Usager & RAG Multilingue (3 min)

**Objectif** : Montrer la fluidité de l'interface, la reconnaissance des intentions et la puissance du moteur IA RAG sur la base documentaire.

* Commencez sur la page d'accueil (Landing Page). Cliquez sur **"Démarrer le Chat"**.
* Montrez l'arborescence native type "WhatsApp" : le menu de bienvenue s'affiche avec les 4 boutons interactifs.
* **Test FR** : Écrivez ou cliquez sur *"Je cherche des informations sur la création d'entreprise"*. Le bot répondra en se basant sur le document ChromaDB.
* **Test Anglais/Arabe** : Écrivez une requête dans une autre langue :
  * _"What are the taxes for setting up an IT company?"_
  * L'IA détectera implicitement l'anglais et générera sa réponse en anglais.
* _Note pour le jury_ : Insistez sur les marqueurs d'engagement (Skeleton Loader pulsatile animé) et le routage des réponses.

### 💼 Scénario 2 : Le Flow Structuré des Incitations (2 min)

**Objectif** : Prouver que l'IA ne fait pas que répondre à main levée, mais peut aussi guider l'utilisateur via des arbres de décisions précis.

* Cliquez sur la suggestion ou tapez *"Quelles sont les incitations et aides disponibles ?"*
* Laissez le bot poser sa première question à choix multiple : *"Secteur d'activité"*.
* Cliquez sur *"🏭 Industrie"* 
* Le fil d'ariane (Breadcrumb) se met à jour : `🏠 Accueil > Incitations > Industrie`.
* Cliquez sur *"🏢 PME"*.
* Montrez que l'utilisateur peut toujours revenir en arrière grâce au bouton *"🔙 Retour"*.
* Finalisez avec la région *"Rabat"*.
* Le bot compile la base locale et ressort le Top 5 des incitations correspondantes.

### 🔒 Scénario 3 : Suivi de Dossier & OTP Sécurisé (3 min)

**Objectif** : Montrer l'interfaçage potentiel avec les SI internes du CRI via Redis Upstash et de la double vérification.

* Tapez *"Suivre mon dossier"*.
* Le bot vous demande la référence.
* Tapez **`INV-2024-001`** (dossier validé) ou **`INV-2024-002`** (dossier en cours).
* Le système déclenchera le SMS/Mail. Dans le cadre de la démo, une **notification Toast/Navigateur** (`🔐 Votre code OTP est...`) apparaîtra. 
* Entrez le nombre à 6 chiffres reçu dans le Chat.
* L'IA dévoilera les informations internes (statut détaillé du dossier, commentaires de la commission).
* _Note pour le jury_ : C'est ce qui différencie un bot générique d'un bot interopérable sécurisé "Enterprise".

### 📊 Scénario 4 : La Tour de Contrôle / Dashboard Admin (4 min)

**Objectif** : Rassurer le jury sur le fait que l'outil est maitrisé et supervisé par les agents du CRI.

* Basculez sur votre second onglet `http://localhost:5173/admin`.
* Montrez la **Vue d'Ensemble** : Le nombre total de messages traités qui vient de s'actualiser, ainsi que le graphique métier Chart.js.
* Allez sur **Messages** : Montrez l'historique complet des discussions tracées (incluant vos propres requêtes passées quelques secondes plus tôt).
* Allez sur **Questions Non Reconnues** : Montrez comment le système remonte les anomalies de l'IA. Un agent peut cliquer sur "Modifier" et soumettre sa propre réponse. *(Mentionnez que cela irait l'indexer dans la base ChromaDB vectorielle ensuite).*
* Allez sur **Suivi Dossiers** : Modifiez le statut d'un des dossiers de *"En cours d'examen"* à *"Validé"*. Lors du clic, montrez au jury que le simulateur lance l'alerte de push notification WhatsApp ciblant l'usager !
* Enfin, rendez-vous sur **Publipostage** : 
  1. Chargez virtuellement un document (cliquez sur l'encart vert).
  2. Sélectionnez "Invitation Événement".
  3. Montrez la 'Preview WhatsApp' à droite reflétant les variables.
  4. Cliquez sur **Diffusion**, montrez l'animation de chargement puis l'écran de succès.

---

## 💡 Astuces & Secours
- **Base ChromaDB (RAG)** : Si le bot répond parfois "Je n'ai pas la réponse", c'est une fonctionnalité (le paramètre `is_fallback` évite les hallucinations). C'est le moment parfait pour montrer que la question tombe dans le panel *Questions Non Reconnues* du Dashboard !
- **Effacer l'historique** : Pour repartir de zéro entre deux rendez-vous avec le jury, actualisez l'application cliente. Pour un grand ménage, vous pouvez vider vos tables Supabase.
- **Réactivité** : L'IHM du chat WhatsApp et du Dashboard ont été conçues pour être montrées de façon dynamique. N'hésitez pas à rafraîchir ou redimensionner la fenêtre si on vous le demande.

**Bonne Démonstration ! 🇲🇦**
