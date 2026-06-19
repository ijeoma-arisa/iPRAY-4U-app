from .database import get_db_connection

def ensure_profile_exists(user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO profiles (id)
                VALUES (%s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (user_id,)
            )