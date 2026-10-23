from starlette.requests import Request

from loggers.logger_req import logger

async def logging_middleware(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code} {response.headers}")
    return response