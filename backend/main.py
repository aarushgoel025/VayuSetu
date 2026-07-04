from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

from ingest import ingest_job
from routes import add_routes_a
from violation_tracker import add_violation_tracker_routes
from legal_advisory import add_legal_advisory_routes

# LAKSHITA'S ROUTER IMPORTS (Person B)
# We assume Lakshita has her own `add_routes_b` function.
try:
    from routes import add_routes_b
except ImportError:
    def add_routes_b(app: FastAPI):
        # Stub function so the app still runs without her code
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start APScheduler
    scheduler = BackgroundScheduler()
    from datetime import datetime
    scheduler.add_job(ingest_job, 'interval', minutes=15, next_run_time=datetime.now())
    scheduler.start()
    
    yield
    
    # Shutdown
    scheduler.shutdown(wait=False)

app = FastAPI(title="VayuSetu Backend", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to VayuSetu API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Add Routes from Person A (Me)
add_routes_a(app)

# Add Routes from Person B (Lakshita)
add_routes_b(app)

# Additional Features
add_violation_tracker_routes(app)
add_legal_advisory_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
