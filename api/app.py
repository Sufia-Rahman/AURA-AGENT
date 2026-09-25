import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .routes import router


APP_VERSION = "1.0.0"


app = FastAPI(
    title="AURA API",
    description=(
        "API layer for AURA — Autonomous "
        "Universal Research & Reasoning Agent."
    ),
    version=APP_VERSION
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def request_id_middleware(
    request: Request,
    call_next
):

    request_id = str(
        uuid.uuid4()
    )

    request.state.request_id = request_id

    response = await call_next(
        request
    )

    response.headers[
        "X-Request-ID"
    ] = request_id

    return response


@app.get("/")
def root():

    return {
        "service": "AURA API",
        "version": APP_VERSION,
        "status": "running",
        "message": (
            "AURA backend is online."
        )
    }


app.include_router(
    router
)