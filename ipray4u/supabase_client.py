import os

from flask import g
from supabase import create_client
from supabase.lib.client_options import SyncClientOptions

SUPABASE_CLIENT_KEY = "supabase_client"

def get_supabase():
    if SUPABASE_CLIENT_KEY not in g:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_PUBLISHABLE_KEY"]

        g.supabase_client = create_client(
            url,
            key,
            options=SyncClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            ),
        )

    return g.supabase_client
