from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.dependencies import get_state
from app.simulation.worker import SimulationWorker
from fastapi.middleware.cors import CORSMiddleware

from app.routes.network import router as network_router
from app.routes.recovery import router as recovery_router
from app.routes.messages import router as messages_router
from app.routes.simulation import router as simulation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker = SimulationWorker(get_state())
    worker.start()
    try:
        yield
    finally:
        worker.stop()


app = FastAPI(
    title="Disaster-Resilient Emergency Communication Network",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(network_router)
app.include_router(recovery_router)
app.include_router(messages_router)
app.include_router(simulation_router)


@app.get("/")
def health_check() -> dict:
    """Return a basic API health response."""

    return {
        "status": "online",
        "service": "disaster-resilient-network",
    }
