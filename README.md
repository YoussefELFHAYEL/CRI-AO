# CRI-RSK Demo Chatbot & Admin Dashboard

Bienvenue dans le dépôt du projet de démonstration pour le **Centre Régional d'Investissement de Rabat-Salé-Kénitra**. Ce système est une preuve de concept avancée intégrant un **Chatbot IA conversationnel (RAG)** et un **Dashboard Administratif complet** simulant des capacités d'entreprise (Enterprise-ready).

---

## 🚀 Vue d'ensemble des Fonctionnalités

### 1. 🤖 Assistant Virtuel Public (Interface WhatsApp Clone)
- **RAG Intelligent Multilingue** : Répond précisément aux questions sur les procédures d'investissement en s'appuyant uniquement sur les documents du CRI.
- **Détection Automatique de la Langue** : Support complet du Français, de l'Anglais et de l'Arabe classique/Darija.
- **Arbre de Décision Dynamique (Incitations)** : Parcours guidé à choix multiples de 3 étapes (Secteur > Taille > Région) interrogeant des métadonnées JSON complexes pour isoler le Top 5 des subventions applicables.
- **Suivi des Dossiers & Double Authentification (OTP)** : Interfaçage simulé avec les SI en backend (via Redis/Upstash), déclenchant l'envoi d'un code de vérification SMS avant la divulgation des données d'un dossier d'investissement.
- **Escalade Humaine Intelligente** : Transfert vers un agent humain si l'IA doute, détecte de l'animosité, ou si l'utilisateur l'exige avec le bouton 4.

### 2. 🛡️ Portail Administrateur (Tours de contrôle)
- **Vue d'Ensemble & Métriques** : KPIs en live (Taux de résolution, volume heure par heure via Chart.js, notes moyennes des utilisateurs).
- **Questions Non Reconnues (Human-in-the-Loop)** : Audit quotidien des réponses à "faible confiance". L'administrateur peut valider, modifier ou rejeter le comportement du bot et écraser l'IA.
- **Base de Connaissances Globale** : Gestion des documents ChromaDB ingérés, et ajout "manuel" de couples Questions/Réponses forcées dans la DB Vectorielle.
- **Suivi Dossiers** : Modification du statut d'un dossier qui déclenche instantanément l'envoi de notification "Push WhatsApp" à l'usager simulé.
- **Publipostage WhatsApp** : Fonctionnalité Business de pointe permettant d'uploader un CSV (liste d'usagers), d'assigner un template (ex: rappel d'événement), de prévisualiser la bulle générée et de simuler la diffusion.
- **CRM Haute-Performance** : Affichage simulé (Mock) gérant visuellement une data-table de 20 000 contacts de sources variées (Faker.js / Pagination experte).

---

## 🧠 Architecture Technique RAG (Retrieval-Augmented Generation)

La brique RAG de l'application est conçue pour être de "Classe Entreprise" et empêcher toute hallucination néfaste pour une institution étatique telle que le CRI.

### 1. Ingestion Documentaire & Stratégie de Chunking
* **Découpage intelligent** : Utilisation de `RecursiveCharacterTextSplitter`.
* **Dimensionnement (Chunk Size & Overlap)** : Les documents (Textes, PDF, JSON) sont divisés en *chunks* de 1000 caractères, avec un chevauchement (*overlap*) de 200 caractères. Cela permet de s'assurer que le contexte clé (comme "Article 4 de la loi bancaire") ne soit jamais séparé sémantiquement de son paragraphe d'application, gardant ainsi une parfaite cohérence logique.

### 2. Architecture "Hybrid Retrieval" (Double Base)
* **Recherche Sémantique (Vecteurs)** : Base Vectorielle locale **ChromaDB** couplée au modèle d'embedding (Google Generative AI). Le RAG "comprend" le sens de la question pour chercher le bon document, même si les mots diffèrent.
* **Recherche Lexicale (Mot-clé Strict)** : Indexation parallèle via **BM25 Okapi** (*Algorithme derrière Elasticsearch*). Gère les acronymes ou les références précises de dossiers que les vecteurs gérent moins bien.
* **Fusion** : La technique avancée du *Fusion Retrieval* combine mathématiquement la base sémantique et la base lexicale lors de la recherche pour minimiser drastiquement le bruit (Rank Fusion Formula).

### 3. Pipeline Temps Réel d'Interrogation
Quand l'utilisateur pose une question complexe :
1. **Query Transform** : Le LLM ré-écrit et purifie la demande de l'utilisateur pour en extraire des mots clés purs avant de l'envoyer aux DB.
2. **Récupération des Candidats (K=5)** : Le *Fusion Retrieval* ramène les 5 meilleurs extraits documentaires du CRI.
3. **Reranking (Cross-Encoder)** : (Si activé dans la configuration). Ces 5 extraits subissent un nouveau tri très strict par un modèle *HuggingFace Cross-Encoder*, afin de sélectionner uniquement le top 3 absolu pour ne pas saturer l'attention de l'IA finale.

### 4. Blocage Anti-Hallucination & Fallback
* Si les scores de pertinence (Cosine Similarity Score de ChromaDB) passent sous le seuil critique pour la question, la variable `is_fallback` est retournée comme `True`. 
* L'IA avoue alors proprement : *"Je n'ai pas pu trouver les informations officielles"*, et la question atterrit directement dans le backoffice Supabase de supervision dans le l'onglet *"Questions Non Reconnues"*.

---

## 🛠️ Stack Technique Majeure

- **Frontend** : **React** (Vite), React-Router, CSS pur (Clone structurel de l'UX WhatsApp Web), Chart.js, Lucide-React.
- **Backend API API** : **Python (FastAPI)**, asynchrone, modulaire et extrêmement rapide.
- **Data Layers** :
  - **Supabase** (PostgreSQL distant) : Historique, Conversations, Questions en attentes.
  - **Upstash / Redis** : Tiers cache pour la tokenisation et génération asynchrone sécurisée d'OTP (5 minutes de vie).
  - **ChromaDB** : Base vectorielle documentaire offline locale pour sécurité maximale des documents critiques.
- **Intelligence Artificielle** : API Google Gemini (LLM & Embedder), LangChain, BM25.
