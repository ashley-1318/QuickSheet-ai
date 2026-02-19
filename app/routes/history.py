from fastapi import APIRouter, Depends, HTTPException

from app.services.supabase_client import supabase
from app.utils.auth import get_current_user_id

router = APIRouter(prefix="/api/v1")


@router.get("/history")
def get_history(user_id: str = Depends(get_current_user_id)) -> list[dict]:
    try:
        result = (
            supabase.table("cheatsheets")
            .select("id, title, one_line_summary, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch history") from exc

    return result.data or []


@router.get("/cheatsheet/{cheatsheet_id}")
def get_cheatsheet(
    cheatsheet_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        result = (
            supabase.table("cheatsheets")
            .select("structured_json")
            .eq("id", cheatsheet_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch cheatsheet") from exc

    if not result.data:
        raise HTTPException(status_code=404, detail="Cheatsheet not found")

    return result.data[0].get("structured_json") or {}


@router.delete("/cheatsheet/{cheatsheet_id}")
def delete_cheatsheet(
    cheatsheet_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        result = (
            supabase.table("cheatsheets")
            .delete()
            .eq("id", cheatsheet_id)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to delete cheatsheet") from exc

    if not result.data:
        raise HTTPException(status_code=404, detail="Cheatsheet not found")

    return {"status": "ok"}
