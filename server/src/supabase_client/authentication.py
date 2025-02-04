from typing import Annotated

from fastapi import Header, HTTPException

from src.supabase_client.client import get_supabase_client


def is_user_authenticated(authorization: Annotated[str, Header()]):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        jwt = authorization[len("Bearer ") :].strip()
        supabase_client = get_supabase_client()
        userResponse = supabase_client.auth.get_user(jwt=jwt)
        if not userResponse:
            raise HTTPException(status_code=401, detail="User not authenticated")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error in authentication: " + str(e)
        )
    return userResponse.user.id
