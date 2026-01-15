# supabase_client.py

import os
from supabase import create_client, Client
from supabase.client import ClientOptions

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("Supabase env vars not set")


def get_supabase_client(access_token: str) -> Client:
    """
    Create a Supabase client authenticated as the current user
    (required for RLS)
    """
    options = ClientOptions(
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    return create_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY,
        options
    )
