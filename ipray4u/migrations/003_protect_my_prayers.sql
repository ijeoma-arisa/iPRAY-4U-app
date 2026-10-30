-- Migration 003: Protect the My Prayers card

BEGIN;


-- Section A: Reserve the My Prayers name and relationship
ALTER TABLE public.people
ADD CONSTRAINT chk_my_prayers_identity
CHECK (
    -- Relationship 4 must be the special My Prayers card.
    (relationship_id = 4 AND name = 'My Prayers')
    OR
    -- Other relationships cannot use the reserved name.
    (relationship_id <> 4 AND lower(btrim(name)) <> 'my prayers')
);


-- Section B: Enforce at most one Me card per user
CREATE UNIQUE INDEX uq_people_one_me_per_user
ON public.people (user_id)
WHERE relationship_id = 4;


-- Section C: Protect My Prayers against updates
CREATE OR REPLACE FUNCTION public.protect_my_prayers_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = ''
AS $$
BEGIN
    -- C1: Prevent changes to an existing My Prayers card's identity.
    IF OLD.relationship_id = 4 THEN
        IF NEW.id IS DISTINCT FROM OLD.id
           OR NEW.name IS DISTINCT FROM OLD.name
           OR NEW.relationship_id IS DISTINCT FROM OLD.relationship_id
           OR NEW.user_id IS DISTINCT FROM OLD.user_id
        THEN
            RAISE EXCEPTION
                'Cannot modify the My Prayers card';
        END IF;
    END IF;

    -- C2: Prevent converting an ordinary person into My Prayers.
    IF OLD.relationship_id <> 4
       AND NEW.relationship_id = 4
    THEN
        RAISE EXCEPTION
            'Cannot convert an existing person into My Prayers';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER protect_my_prayers_update_trigger
BEFORE UPDATE ON public.people
FOR EACH ROW
EXECUTE FUNCTION public.protect_my_prayers_update();


-- Section D: Protect My Prayers against deletion
-- DRAFT: Verify behavior against actual staging account-deletion cascades.

CREATE OR REPLACE FUNCTION public.protect_my_prayers_delete()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    -- Allow deletion only when the owning auth user is no longer visible.
    IF OLD.relationship_id = 4
       AND EXISTS (
           SELECT 1
           FROM auth.users
           WHERE id = OLD.user_id
       )
    THEN
        RAISE EXCEPTION
            'Cannot delete My Prayers while the auth user exists';
    END IF;

    RETURN OLD;
END;
$$;

CREATE TRIGGER protect_my_prayers_delete_trigger
BEFORE DELETE ON public.people
FOR EACH ROW
EXECUTE FUNCTION public.protect_my_prayers_delete();


-- Section E: Protect the reserved Me relationship
-- E1: Reserve the Me relationship ID and normalized name.
ALTER TABLE public.relationships
ADD CONSTRAINT chk_reserved_me_relationship
CHECK (
    (id = 4 AND relationship = 'Me')
    OR
    (id <> 4 AND lower(btrim(relationship)) <> 'me')
);

-- E2: Prevent updates or deletion of the reserved Me relationship.
CREATE OR REPLACE FUNCTION public.protect_me_relationship()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = ''
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF OLD.id = 4 THEN
            RAISE EXCEPTION
                'Cannot delete the reserved Me relationship';
        END IF;

        RETURN OLD;
    END IF;

    IF TG_OP = 'UPDATE' THEN
        IF (OLD.id = 4 OR NEW.id = 4)
           AND (
               NEW.id IS DISTINCT FROM OLD.id
               OR NEW.relationship IS DISTINCT FROM OLD.relationship
           )
        THEN
            RAISE EXCEPTION
                'Cannot modify the reserved Me relationship';
        END IF;

        RETURN NEW;
    END IF;

    RAISE EXCEPTION 'Unsupported operation: %', TG_OP;
END;
$$;

CREATE TRIGGER protect_me_relationship_trigger
BEFORE UPDATE OR DELETE ON public.relationships
FOR EACH ROW
EXECUTE FUNCTION public.protect_me_relationship();


COMMIT;