from fastapi import FastAPI  # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware  # pyright: ignore[reportMissingImports]

from app.core.config import settings
from app.db.base import Base  # noqa: F401
from app.db.session import engine
from app.routers import auth_router, billing_router, clients_vendors_router, contracts_router, demo_router, stats_router, trips_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(clients_vendors_router.router, prefix="", tags=["Clients & Vendors"])
app.include_router(contracts_router.router, prefix="/contracts", tags=["Contracts"])
app.include_router(trips_router.router, prefix="/trips", tags=["Trips"])
app.include_router(billing_router.router, prefix="/billing", tags=["Billing"])
app.include_router(stats_router.router, prefix="/stats", tags=["Statistics"])
# app.include_router(demo_router.router, prefix="", tags=["Demo"])  # DISABLED - Using real endpoints


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
