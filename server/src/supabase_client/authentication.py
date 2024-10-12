from fastapi import HTTPException

from src.supabase_client.client import get_supabase_client


def is_user_authenticated():
    try:
        supabase_client = get_supabase_client()
        user = supabase_client.auth.get_user()
        if not user:
            raise HTTPException(status_code=401, detail="User not authenticated")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error in authentication: " + str(e)
        )
    return True
