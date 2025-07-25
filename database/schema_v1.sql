-- schema_v1.sql

-- Table pour stocker les profils des utilisateurs
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY, -- Référence à l'ID de l'utilisateur (ex: de Supabase Auth)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Les préférences et allergies seront stockées dans un format JSONB pour plus de flexibilité
    profile_data JSONB NOT NULL
);

-- Table pour l'historique des scans de chaque utilisateur
CREATE TABLE scan_history (
    scan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    product_barcode TEXT NOT NULL,
    scan_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Résultat de l'analyse contextuelle (Compatible, Avertissement, Incompatible)
    verdict VARCHAR(50) NOT NULL
);

-- Table pour les contributions de la communauté (ajout de produits, etc.)
CREATE TABLE community_contributions (
    contribution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    contribution_type VARCHAR(50) NOT NULL, -- ex: 'NEW_PRODUCT', 'CORRECTION'
    data JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING_VALIDATION', -- PENDING, APPROVED, REJECTED
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);