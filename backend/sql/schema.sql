-- CRI-RSK Chatbot — Supabase Schema
-- Run this SQL in the Supabase SQL Editor to create all tables.

-- ============================================
-- Core Tables
-- ============================================

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_type TEXT NOT NULL CHECK (agent_type IN ('public', 'internal')),
    user_phone TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    language TEXT DEFAULT 'fr'
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'bot')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    language TEXT
);

CREATE TABLE IF NOT EXISTS unknown_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    suggested_answer TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'validated', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    validated_answer TEXT,
    validated_by TEXT
);

CREATE TABLE IF NOT EXISTS ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    score INT NOT NULL CHECK (score >= 1 AND score <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS faq_validated (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    language TEXT DEFAULT 'fr',
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Demo Tables
-- ============================================

CREATE TABLE IF NOT EXISTS demo_statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    period TEXT,  -- 'today', 'week', 'month', 'year'
    category TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS demo_dossiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference TEXT UNIQUE NOT NULL,  -- e.g. 'INV-2024-001'
    company_name TEXT NOT NULL,
    project_type TEXT NOT NULL,
    status TEXT NOT NULL,
    current_step TEXT,
    total_steps INT DEFAULT 5,
    completed_steps INT DEFAULT 0,
    investor_name TEXT,
    investor_phone TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    history JSONB DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS administrators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    entity TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    company TEXT,
    sector TEXT,
    source TEXT DEFAULT 'chatbot',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Indexes
-- ============================================

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_ratings_message_id ON ratings(message_id);
CREATE INDEX IF NOT EXISTS idx_dossiers_reference ON demo_dossiers(reference);
CREATE INDEX IF NOT EXISTS idx_dossiers_status ON demo_dossiers(status);
CREATE INDEX IF NOT EXISTS idx_statistics_period ON demo_statistics(period);
CREATE INDEX IF NOT EXISTS idx_contacts_source ON contacts(source);
CREATE INDEX IF NOT EXISTS idx_unknown_questions_status ON unknown_questions(status);

-- ============================================
-- Row Level Security (basic — open for demo)
-- ============================================

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE unknown_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE faq_validated ENABLE ROW LEVEL SECURITY;
ALTER TABLE demo_statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE demo_dossiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE administrators ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

-- Allow all operations via anon key (demo mode)
CREATE POLICY "Allow all for anon" ON conversations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON messages FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON unknown_questions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON ratings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON faq_validated FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON demo_statistics FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON demo_dossiers FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON administrators FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for anon" ON contacts FOR ALL USING (true) WITH CHECK (true);
