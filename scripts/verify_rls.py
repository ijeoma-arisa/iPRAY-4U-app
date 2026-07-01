"""Integration test for the staging Supabase Row-Level Security policies.

This script loads .env.staging directly, then verifies the loaded Supabase URL
matches the known staging project before creating any fixtures.
"""

import os
import sys
from uuid import uuid4

from postgrest.exceptions import APIError
from supabase import Client, create_client
from dotenv import load_dotenv

load_dotenv(".env.staging", override=True)

STAGING_SUPABASE_URL = "https://mrawhknpzsnapjjyiwpf.supabase.co"
REQUIRED_ENV_VARS = (
    "SUPABASE_URL",
    "SUPABASE_PUBLISHABLE_KEY",
    "AMAKA_EMAIL",
    "AMAKA_PASSWORD",
    "EBUKA_EMAIL",
    "EBUKA_PASSWORD",
)


class TestFailure(Exception):
    """Stop the test at its first failed assertion."""


class Results:
    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: str | None = None

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.failed = message
            raise TestFailure(message)

    def passed_test(self, message: str) -> None:
        self.passed.append(message)
        print(f"PASS: {message}")

    def summary(self, cleanup_warning: str | None = None) -> None:
        print("\n=== RLS TEST SUMMARY ===")
        print(f"Passed: {len(self.passed)}")
        if self.failed:
            print("RLS result: FAIL")
            print(f"FAIL: {self.failed}")
        else:
            print("RLS result: PASS")
        if cleanup_warning:
            print(f"CLEANUP WARNING: {cleanup_warning}")


def validate_environment() -> None:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise TestFailure(
            "Missing required environment variables: " + ", ".join(missing)
        )

    # Refuse to create fixtures unless the configured URL is the known staging
    # project. A trailing slash is ignored, but no other URL is accepted.
    actual_url = os.environ["SUPABASE_URL"].rstrip("/")
    if actual_url != STAGING_SUPABASE_URL:
        raise TestFailure(
            "Safety check failed: SUPABASE_URL is not the staging Supabase URL"
        )


def new_client() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"], os.environ["SUPABASE_PUBLISHABLE_KEY"]
    )


def sign_in(email_var: str, password_var: str) -> tuple[Client, str]:
    """Authenticate a dedicated client so its table requests use this JWT."""
    client = new_client()
    response = client.auth.sign_in_with_password(
        {"email": os.environ[email_var], "password": os.environ[password_var]}
    )
    if response.user is None or response.session is None:
        raise TestFailure(f"Supabase Auth did not return a session for {email_var}")
    return client, response.user.id


def select_all(client: Client, table: str) -> list[dict]:
    return client.table(table).select("*").execute().data or []


def test_relationship_reads(
    results: Results, label: str, client: Client
) -> list[dict]:
    # Authenticated users need relationship IDs to create their people.
    relationships = select_all(client, "relationships")
    results.require(
        relationships != [], f"{label} can read relationships while authenticated"
    )
    results.passed_test(f"{label} can read relationships while authenticated")
    return relationships


def create_fixtures(
    client: Client, user_id: str, relationship_id: int, label: str
) -> dict:
    """Create one temporary person and prayer owned by the signed-in user."""
    token = uuid4()
    people = (
        client.table("people")
        .insert(
            {
                "name": f"rls-{label}-person-{token}",
                "relationship_id": relationship_id,
                "user_id": user_id,
            }
        )
        .execute()
        .data
        or []
    )
    if not people:
        raise TestFailure(f"Could not create the temporary {label} person")

    person = people[0]
    prayers = (
        client.table("prayers")
        .insert(
            {
                "person_id": person["id"],
                "prayer": f"Temporary RLS prayer {token}",
                "has_prayed": False,
            }
        )
        .execute()
        .data
        or []
    )
    if not prayers:
        # This fixture is registered by the caller only after this function
        # returns, so clean up a partially created fixture here.
        client.table("people").delete().eq("id", person["id"]).execute()
        raise TestFailure(f"Could not create the temporary {label} prayer")

    return {"client": client, "person": person, "prayer": prayers[0]}


def cleanup_fixtures(fixtures: list[dict]) -> None:
    """Remove all temporary rows, even when an assertion failed."""
    errors = []
    for fixture in reversed(fixtures):
        client = fixture["client"]
        try:
            client.table("prayers").delete().eq(
                "id", fixture["prayer"]["id"]
            ).execute()
            client.table("people").delete().eq(
                "id", fixture["person"]["id"]
            ).execute()
        except Exception as error:  # Preserve cleanup attempts for other fixtures.
            errors.append(str(error))
    if errors:
        raise RuntimeError("Fixture cleanup failed: " + "; ".join(errors))


def test_profile_reads(
    results: Results,
    label: str,
    client: Client,
    user_id: str,
    other_user_id: str,
) -> None:
    # A broad SELECT should expose exactly the signed-in user's profile.
    profiles = select_all(client, "profiles")
    results.require(
        len(profiles) == 1 and profiles[0]["id"] == user_id,
        f"{label} can read only their own profile",
    )
    other = (
        client.table("profiles").select("*").eq("id", other_user_id).execute().data
        or []
    )
    results.require(other == [], f"{label} cannot read the other user's profile")
    results.passed_test(f"{label} can read only their own profile")


def test_people_reads(
    results: Results,
    label: str,
    client: Client,
    user_id: str,
    own_person: dict,
    other_person: dict,
) -> None:
    # The user's seeded person must be readable, and every visible row must be
    # owned by that user even if unrelated staging data already exists.
    people = select_all(client, "people")
    results.require(
        any(row["id"] == own_person["id"] for row in people)
        and all(row["user_id"] == user_id for row in people),
        f"{label} can read only their own people",
    )
    other = (
        client.table("people")
        .select("*")
        .eq("id", other_person["id"])
        .execute()
        .data
        or []
    )
    results.require(other == [], f"{label} cannot read the other user's person")
    results.passed_test(f"{label} can read only their own people")


def test_prayer_reads(
    results: Results,
    label: str,
    client: Client,
    own_prayer: dict,
    other_prayer: dict,
) -> None:
    # The seeded prayer must be readable, and every visible prayer must belong to
    # one of the signed-in user's visible people.
    prayers = select_all(client, "prayers")
    own_person_ids = {person["id"] for person in select_all(client, "people")}
    results.require(
        any(row["id"] == own_prayer["id"] for row in prayers),
        f"{label} can read their own prayers",
    )
    results.require(
        all(row["person_id"] in own_person_ids for row in prayers),
        f"{label} can read only prayers belonging to their own people",
    )

    # The other user's known fixture prayer ID must remain hidden.
    other = (
        client.table("prayers")
        .select("*")
        .eq("id", other_prayer["id"])
        .execute()
        .data
        or []
    )
    results.require(other == [], f"{label} cannot read the other user's prayers")
    results.passed_test(f"{label} can read only their own prayers")


def test_cross_user_writes(
    results: Results,
    attacker_label: str,
    attacker: Client,
    owner: Client,
    owner_id: str,
    target_person: dict,
    target_prayer: dict,
) -> None:
    marker = f"rls-forbidden-{uuid4()}"

    # Inserting a person with the other user's user_id must error or insert no row.
    try:
        attacker.table("people").insert(
            {
                "name": marker,
                "relationship_id": target_person["relationship_id"],
                "user_id": owner_id,
            }
        ).execute()
    except APIError:
        pass
    inserted = owner.table("people").select("id").eq("name", marker).execute().data or []
    for row in inserted:  # Clean up before reporting a broken INSERT policy.
        owner.table("people").delete().eq("id", row["id"]).execute()
    results.require(
        inserted == [], f"{attacker_label} cannot insert a person for the other user"
    )
    results.passed_test(f"{attacker_label} cannot insert a person for the other user")

    # Updating the other user's known temporary person must not change it.
    try:
        attacker.table("people").update({"name": marker}).eq(
            "id", target_person["id"]
        ).execute()
    except APIError:
        pass
    current = (
        owner.table("people").select("name").eq("id", target_person["id"]).execute().data
        or []
    )
    results.require(
        current and current[0]["name"] == target_person["name"],
        f"{attacker_label} cannot update another user's person",
    )
    results.passed_test(f"{attacker_label} cannot update another user's person")

    # Deleting the other user's known temporary person must leave it present.
    try:
        attacker.table("people").delete().eq("id", target_person["id"]).execute()
    except APIError:
        pass
    current = (
        owner.table("people").select("id").eq("id", target_person["id"]).execute().data
        or []
    )
    results.require(
        current != [], f"{attacker_label} cannot delete another user's person"
    )
    results.passed_test(f"{attacker_label} cannot delete another user's person")

    # Updating the other user's known temporary prayer must not change it.
    try:
        attacker.table("prayers").update({"prayer": marker}).eq(
            "id", target_prayer["id"]
        ).execute()
    except APIError:
        pass
    current = (
        owner.table("prayers")
        .select("prayer, has_prayed, person_id")
        .eq("id", target_prayer["id"])
        .execute()
        .data
        or []
    )
    results.require(
        current
        and current[0]["prayer"] == target_prayer["prayer"]
        and current[0]["has_prayed"] == target_prayer["has_prayed"]
        and current[0]["person_id"] == target_prayer["person_id"],
        f"{attacker_label} cannot update another user's prayer",
    )
    results.passed_test(f"{attacker_label} cannot update another user's prayer")

    # Deleting the other user's known temporary prayer must leave it present.
    try:
        attacker.table("prayers").delete().eq("id", target_prayer["id"]).execute()
    except APIError:
        pass
    current = (
        owner.table("prayers")
        .select("id")
        .eq("id", target_prayer["id"])
        .execute()
        .data
        or []
    )
    results.require(
        current != [], f"{attacker_label} cannot delete another user's prayer"
    )
    results.passed_test(f"{attacker_label} cannot delete another user's prayer")


def test_anonymous_reads(results: Results) -> None:
    anonymous = new_client()
    # The publishable key alone must expose no protected rows.
    for table in ("profiles", "people", "prayers"):
        try:
            visible = select_all(anonymous, table)
        except APIError:
            visible = []
        results.require(visible == [], f"Anonymous users cannot read {table}")
        results.passed_test(f"Anonymous users cannot read {table}")


def run_tests(results: Results, fixtures: list[dict]) -> None:
    validate_environment()
    amaka, amaka_id = sign_in("AMAKA_EMAIL", "AMAKA_PASSWORD")
    ebuka, ebuka_id = sign_in("EBUKA_EMAIL", "EBUKA_PASSWORD")
    results.require(amaka_id != ebuka_id, "The two staging users must be different")

    amaka_relationships = test_relationship_reads(results, "Amaka", amaka)
    ebuka_relationships = test_relationship_reads(results, "Ebuka", ebuka)

    # Both accounts create their own isolated test records; no existing people or
    # prayers are required for any assertion.
    amaka_fixture = create_fixtures(
        amaka, amaka_id, amaka_relationships[0]["id"], "amaka"
    )
    fixtures.append(amaka_fixture)
    ebuka_fixture = create_fixtures(
        ebuka, ebuka_id, ebuka_relationships[0]["id"], "ebuka"
    )
    fixtures.append(ebuka_fixture)

    test_profile_reads(results, "Amaka", amaka, amaka_id, ebuka_id)
    test_profile_reads(results, "Ebuka", ebuka, ebuka_id, amaka_id)
    test_people_reads(
        results,
        "Amaka",
        amaka,
        amaka_id,
        amaka_fixture["person"],
        ebuka_fixture["person"],
    )
    test_people_reads(
        results,
        "Ebuka",
        ebuka,
        ebuka_id,
        ebuka_fixture["person"],
        amaka_fixture["person"],
    )
    test_prayer_reads(
        results,
        "Amaka",
        amaka,
        amaka_fixture["prayer"],
        ebuka_fixture["prayer"],
    )
    test_prayer_reads(
        results,
        "Ebuka",
        ebuka,
        ebuka_fixture["prayer"],
        amaka_fixture["prayer"],
    )
    test_cross_user_writes(
        results,
        "Amaka",
        amaka,
        ebuka,
        ebuka_id,
        ebuka_fixture["person"],
        ebuka_fixture["prayer"],
    )
    test_cross_user_writes(
        results,
        "Ebuka",
        ebuka,
        amaka,
        amaka_id,
        amaka_fixture["person"],
        amaka_fixture["prayer"],
    )
    test_anonymous_reads(results)


def main() -> int:
    results = Results()
    fixtures: list[dict] = []
    cleanup_warning = None
    exit_code = 0
    try:
        run_tests(results, fixtures)
    except TestFailure as error:
        results.failed = results.failed or str(error)
        exit_code = 1
    except Exception as error:
        results.failed = f"Unexpected integration-test error: {error}"
        exit_code = 1
    finally:
        try:
            cleanup_fixtures(fixtures)
        except Exception as error:
            cleanup_warning = str(error)
            exit_code = 1

    results.summary(cleanup_warning)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
