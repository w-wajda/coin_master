from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer
from app.presentation.endpoints.users import routes as users_routes

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/health/")
@router.get("/healthz/")
async def health():
    return {"status": "ok"}


@router.get("/sentry-debug/")
async def trigger_error():
    division_by_zero = 1 / 0
    return division_by_zero


@router.get("/version/")
async def version():
    return {"version": "0.1.0"}


router.include_router(users_routes, prefix="/v2/users", dependencies=[Depends(security)])
router.include_router(tokens_routes, prefix="/v2/tokens", dependencies=[Depends(security)])

