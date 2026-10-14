-- Migration 002: Add the Me relationship
-- Feature: Me / My Prayers

BEGIN;

INSERT INTO public.relationships (id, relationship)
VALUES (4, 'Me');

COMMIT;
