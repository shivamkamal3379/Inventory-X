from fastapi import FastAPI
from src.core.database import engine, Base
from src.routers import agents, items, parties, rent, returns
from src.core.config import settings

# Create tables
# Import all models to ensure they are registered with Base
from src.models import auth, people, inventory, transactions

Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Inventory X API",
    version="1.0.0",
    description="Backend API for Inventory X / RentalPro",
)

# Include Routers
app.include_router(agents.router)
app.include_router(items.router)
app.include_router(parties.router)
app.include_router(rent.router)
app.include_router(returns.router)


# Root health-check endpoint
@app.get("/")
def root():
    return {"status": "running", "app": "Inventory X Backend"}
