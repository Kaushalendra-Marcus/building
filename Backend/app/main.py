from fastapi import FastAPI
from app.config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"________Starting {settings.APP_NAME}......__________")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}......")


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    logger.info("Root endpoint hit")
    return {"message": f"{settings.APP_NAME} is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
