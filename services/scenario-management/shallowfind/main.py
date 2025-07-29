from fastapi import FastAPI
from shallowfind.modules.auth.router import router as auth_router
from shallowfind.modules.users.router import router as user_router
from shallowfind.modules.scenarios.router import router as scenario_router

import strawberry
from strawberry.fastapi import GraphQLRouter
from .graphql.queries import Query


schema = strawberry.Schema(query=Query)

graphql_app = GraphQLRouter(schema)

app = FastAPI(
    title="Shallowfind",
    description="Lifetime financial planning API",
    version="0.0.1a",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(scenario_router, prefix="/api/scenarios", tags=["Scenarios"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Shallowfind API!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
