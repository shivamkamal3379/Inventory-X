from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import engine, Base
from src.routers import agents, items, parties, rent, returns, prices, dashboard, auth
from src.core.config import settings

# Create tables
# Import all models to ensure they are registered with Base
from src.models import auth as auth_models, people, inventory, transactions

Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Inventory X API",
    version="1.0.0",
    description="Backend API for Inventory X / RentalPro",
)

# CORS Middleware — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(items.router)
app.include_router(parties.router)
app.include_router(rent.router)
app.include_router(returns.router)
app.include_router(prices.router)
app.include_router(dashboard.router)


# Root health-check endpoint
@app.get("/")
def root():
    return {"status": "running", "app": "Inventory X Backend"}
