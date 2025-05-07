import re
import time
from typing import Callable

from fastapi import Request, Response  # , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
# from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse


async def check_name_format(request: Request, call_next: Callable) -> Response:
    path_parts = request.scope["path"].split("/")
    if path_parts[-2] == "hello":
        if not re.match("^[a-zA-Zа-яА-Я]{2,30}$", path_parts[-1]):
            # print('Catch in check_name_format middleware')
            return JSONResponse(
                status_code=400,
                content={"detail": "Name must be in regex ^[a-zA-Zа-яА-Я]{2,30}$"},
            )

            # this make traceback and 500
            # raise HTTPException(
            #     status_code=400,
            #     detail={"message": "Name must be in regex ^[a-zA-Zа-яА-Я]{2,30}$"},
            # )
    response = await call_next(request)
    return response


# must be as first middleware
async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    start_time = time.perf_counter()
    # print('Its in process_time_header request')
    response = await call_next(request)
    # print('Its in process_time_header response')
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Root-Path"] = request.scope.get("root_path")
    return response


middlewares = [
    # (class, arguments for init, params)
    (BaseHTTPMiddleware, (), {"dispatch": add_process_time_header}),
    # (HTTPSRedirectMiddleware, (), {}),
    # (TrustedHostMiddleware, (), {"allowed_hosts": ["127.0.0.1", ]}),  # , "*.example.com", "localhost"])
    (CORSMiddleware, (), {
        "allow_origins": ["http://example.com"],
        "allow_credentials": True,
        "allow_methods": ["POST"],  # "GET",
        "allow_headers": ["*"],
    }),
    (BaseHTTPMiddleware, (), {"dispatch": check_name_format}),
]


class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Pre-processing logic
        # e.g., Authentication, Logging, Metrics
        # print('Its in CustomMiddleware request')
        response = await call_next(request)
        # Post-processing logic
        # e.g., Error Handling, Response Transformation
        # print('Its in CustomMiddleware response')
        return response
