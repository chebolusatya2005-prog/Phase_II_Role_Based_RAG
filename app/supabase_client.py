from supabase import create_client, Client

from app.config import SUPABASE_URL, SUPABASE_KEY


def get_supabase_client() -> Client:
    """Create and return a Supabase client."""

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase URL or key is missing from .env"
        )

    return create_client(SUPABASE_URL, SUPABASE_KEY)