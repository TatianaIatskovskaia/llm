from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from middlewares.logging_middleware import logging_middleware
from routes.travel_routes import router

app = FastAPI()

app.middleware("http")(logging_middleware)

app.include_router(router)