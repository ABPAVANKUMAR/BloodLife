from app.api.notifications import router as notifications_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.donors import router as donors_router

from app.db.database import create_tables
from app.api.blood_requests import router as requests_router


app = FastAPI(
    title="BloodLife API",
    description="Community Blood Donor Registry and Emergency Request System",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(auth_router)
app.include_router(donors_router)
app.include_router(requests_router)
app.include_router(notifications_router)

@app.on_event("startup")
def startup_event():
    create_tables()


@app.get("/")
def root():
    return {
        "message": "Welcome to BloodLife API",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {
        "ok": True,
        "service": "BloodLife API",
        "version": "1.0.0"
    }
