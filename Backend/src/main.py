from fastapi import FastAPI

# Importing DATABASE_URL only to verify env loading (temporary)
from core.config import DATABASE_URL

# Create FastAPI app
app = FastAPI(
    title="Inventory X API",
    version="1.0.0",
    description="Backend API for Inventory X / RentalPro"
)

# Temporary startup check (you can remove later)
@app.on_event("startup")
def startup_event():
    print("✅ Backend starting...")
    print("✅ DATABASE_URL loaded:", DATABASE_URL)


# Root health-check endpoint
@app.get("/")
def root():
    return {
        "status": "running",
        "app": "Inventory X Backend"
    }
