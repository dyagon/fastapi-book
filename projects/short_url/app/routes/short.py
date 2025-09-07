from fastapi import APIRouter, Depends, BackgroundTasks

from fastapi.responses import RedirectResponse, PlainTextResponse
from ..depends import get_short_service, ShortService

router_short = APIRouter(tags=["short_url"])

@router_short.get("/{short_tag}")
async def short_redirect(
    *,
    short_tag: str,
    short_service: ShortService = Depends(get_short_service),
    tasks: BackgroundTasks,
):

    data = await short_service.get_short_url(short_tag)
    if not data:
        return PlainTextResponse("Short URL not found", status_code=404)

    data.visits_count += 1
    tasks.add_task(
        short_service.update_short_url, data.id, visits_count=data.visits_count
    )
    return RedirectResponse(data.long_url)
