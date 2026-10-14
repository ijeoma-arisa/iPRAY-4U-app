-- Migration 001: Add prayer creation timestamps
-- Historical migration: already applied

ALTER TABLE prayers 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ;

ALTER TABLE prayers 
ALTER COLUMN created_at SET DEFAULT NOW();