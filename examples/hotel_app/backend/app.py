from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from backend.routes.reservations import router as reservations_router
from backend.routes.service_orders import router as service_orders_router
from backend.db.db_init import initialize_database  # Import the initialization function

# logger = SetupLogging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager: runs any startup/shutdown logic if needed.
    """
    # STARTUP LOGIC
    print("Initializing in-memory SQLite database...")
    await initialize_database()  # Initialize the database when the app starts
    
    yield
    # SHUTDOWN LOGIC
    # Nothing to do for in-memory DB as it disappears when app stops

def create_app() -> FastAPI:
    # logger.info(f'!!! Starting App: agent poc !!!')
    
    # Allowed CORS origins
    # allowed_origins_str = config.get('domains', 'allowed_origins', fallback='')
    # allowed_origins_list = [
    #     origin.strip()
    #     for origin in allowed_origins_str.split(',')
    #     if origin.strip()
    # ]
    
    middleware = [
        Middleware(
            CORSMiddleware,
            # allow_origins=allowed_origins_list,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*']
        )
    ]
    
    app = FastAPI(
        title="agent poc api",
        version="1.0.0",
        docs_url="/docs",
        description="api for pydantic ai agent poc",
        lifespan=lifespan,
        middleware=middleware
    )
    
    app.include_router(reservations_router)
    app.include_router(service_orders_router)
    
    # 10) Minimal 400 handler for pydantic validation
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder({"detail": "Invalid request body"})
        )
    
    # 11) Health check route
    @app.get("/ping")
    async def ping():
        return JSONResponse(status_code=200, content={"message": "pong"})
    
    return app