from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from supabase._sync.client import SyncClient

from src.database import read_db
from src.supabase_client.authentication import is_user_authenticated
from src.supabase_client.client import get_supabase_client

router = APIRouter(tags=["Authentication"])


@router.get("/authentication/callback", name="/authentication/callback")
def callback(
    code: str, supabase_client: Annotated[SyncClient, Depends(get_supabase_client)]
):
    try:
        supabase_client.auth.exchange_code_for_session({"auth_code": code})
        return RedirectResponse(url="http://localhost:8000/docs")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error in callback: " + str(e))


@router.post("/authentication/sign_in")
def sign_in(supabase_client: Annotated[SyncClient, Depends(get_supabase_client)]):
    try:
        response = supabase_client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirect_to": "http://localhost:8000/authentication/callback"
                },
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error signing user in: " + str(e))
    return {"Sign In With Google Here": response.url}


@router.post("/authentication/sign_out")
def sign_out(supabase_client: Annotated[SyncClient, Depends(get_supabase_client)]):
    try:
        supabase_client.auth.sign_out()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error signing out user: " + str(e))
    return {"message": "User signed out successfully"}


@router.get("/authentication/get_heroes")
def get_heroes(user_id: Annotated[str, Depends(is_user_authenticated)]):
    try:
        print('User_id: ', user_id)
        response = read_db()
        heroes = response.data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error in getting heroes: " + str(e)
        )
    return JSONResponse(content=heroes)
