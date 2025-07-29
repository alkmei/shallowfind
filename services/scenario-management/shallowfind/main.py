from fastapi import FastAPI
from shallowfind.modules.scenarios.router import router as scenario_router

app = FastAPI(
    title="Shallowfind",
    description="Lifetime financial planning API",
    version="0.0.1a",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(scenario_router, prefix="/api/scenarios", tags=["Scenarios"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Shallowfind API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
