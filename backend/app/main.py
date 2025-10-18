from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import requirements, sys2_requirements, testcases

app = FastAPI(title="Requirement Test Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requirements.router)
app.include_router(requirements.req_router)
app.include_router(sys2_requirements.router)
app.include_router(testcases.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Requirement Test Management API"}