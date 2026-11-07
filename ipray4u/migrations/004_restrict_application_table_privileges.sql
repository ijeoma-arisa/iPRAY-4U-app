-- Migration 004: Restrict application table privileges
-- Remove unnecessary TRIGGER and TRUNCATE privileges
-- from anon and authenticated on application tables.

BEGIN;

SET LOCAL lock_timeout = '5s';

REVOKE TRIGGER, TRUNCATE
ON TABLE
    public.people,
    public.prayers,
    public.profiles,
    public.relationships
FROM anon, authenticated;

COMMIT;
