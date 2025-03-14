from fastapi import APIRouter

from backend.api.chat.routes import router as chat_router
from backend.api.auth.routes import router as auth_router
from backend.api.kbase.routes import router as kbase_router
from backend.api.session.routes import router as session_router
from backend.api.assistant.routes import router as assistant_router
from backend.api.account.routes import router as account_router
from backend.api.index.routes import router as index_router


router = APIRouter(prefix="/opsloom-api/v1")


router.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"],
)


router.include_router(
    auth_router,
    prefix="",
    tags=["Auth"],
)

router.include_router(
    kbase_router,
    prefix="/kbase",
    tags=["KBase"],
)

router.include_router(
    session_router,
    prefix="/chat/session",
    tags=["Session"],
)


router.include_router(
    assistant_router,
    prefix="/assistant",
    tags=["Assistant"],
)

router.include_router(
    account_router,
    prefix="/account",
    tags=["Account"],
)

router.include_router(
    index_router,
    prefix="/index",
    tags=["Index"],
)