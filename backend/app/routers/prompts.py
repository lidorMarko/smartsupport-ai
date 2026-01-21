from fastapi import APIRouter
from app.prompts import get_all_prompts_metadata, SYSTEM_PROMPTS

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("")
async def get_prompts():
    """Get all available system prompts for the dropdown."""
    return get_all_prompts_metadata()


@router.get("/{prompt_key}")
async def get_prompt_detail(prompt_key: str):
    """Get full details of a specific prompt (for viewing/editing)."""
    if prompt_key in SYSTEM_PROMPTS:
        return {
            "key": prompt_key,
            **SYSTEM_PROMPTS[prompt_key]
        }
    return {"error": "Prompt not found"}
