import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import webhook, users, matches
from app.mcp_server import mcp


# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables in database if they don't exist
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully.")
    yield
    # Shutdown: Clean up connections if necessary
    logger.info("Shutting down application...")
    await engine.dispose()

app = FastAPI(
    title="Wasportly API",
    description="Backend API supporting the Wasportly WhatsApp assistant and web platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(webhook.router)
app.include_router(users.router)
app.include_router(matches.router)


# Mount the MCP server's SSE application
app.mount("/mcp", mcp.sse_app())


@app.get("/")
async def root():
    return {
        "app": "Wasportly Backend",
        "status": "healthy",
        "version": "1.0.0",
        "docs_url": "/docs"
    }
