from fastapi import HTTPException
from supabase import ClientOptions, create_client

from src.settings import SUPABASE_KEY, SUPABASE_URL

supabase_client = None


def init_supabase_client():
    global supabase_client
    supabase_client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=ClientOptions(flow_type="pkce"),  # For server side auth
    )
    print("Super client initialized", str(supabase_client))


def get_supabase_client():
    """
    Get the supabase client
    """
    try:
        if supabase_client is None:
            init_supabase_client()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error in getting supabase client: " + str(e)
        )
    return supabase_client
