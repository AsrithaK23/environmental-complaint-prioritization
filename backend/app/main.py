from fastapi import FastAPI
from backend.app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from backend.app.admin.routes import (
    router as admin_router,
    users_router,
    analytics_router,
)
from backend.app.auth.routes import router as auth_router
from backend.app.complaints.routes import (
    router as complaints_router,
    staff_router,
)

app = FastAPI(
    title="Environmental Complaint Prioritization API",
    version="1.0.0",
)

origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(complaints_router, prefix="/api")
app.include_router(staff_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")



@app.get("/api/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

from backend.app.complaints.routes import (
    router as complaints_router,
    staff_router,
)