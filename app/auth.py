
"""
Supabase Authentication and Role Verification.
"""

from fastapi import HTTPException, status

from app.supabase_client import get_supabase_client
from app.security import validate_role


def get_current_user(access_token: str):
    """Verify Supabase token and retrieve the user's role."""

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is required."
        )

    supabase = get_supabase_client()

    # Step 1: Verify the access token with Supabase Auth
    try:
        auth_response = supabase.auth.get_user(access_token)
        auth_user = auth_response.user

        if not auth_user:
            raise ValueError("Invalid user")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token."
        )

    # Step 2: Use the user's JWT for database access.
    # This allows existing RLS policies to control access.
    supabase.postgrest.auth(access_token)

    # Step 3: Retrieve the user's profile and role
    try:
        result = (
            supabase.table("users")
            .select("id, email, role, full_name")
            .eq("id", str(auth_user.id))
            .single()
            .execute()
        )

        profile = result.data

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unable to access your user profile. Check database permissions and RLS policies."
        )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found."
        )

    # Step 4: Validate the actual database role
    role = validate_role(profile.get("role"))

    return {
        "user_id": str(auth_user.id),
        "email": profile.get("email"),
        "full_name": profile.get("full_name"),
        "role": role.value
    }
