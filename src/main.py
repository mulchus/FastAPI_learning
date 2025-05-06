import exceptions
from database import DBModel, engine
from env_settings import AppEnvSettings
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from middlewares import middlewares
from starlette.exceptions import HTTPException as StarletteHTTPException
from version import __version__

from users.views import router as user_router
from views.background_tasks import router as background_tasks_router
from views.calc_views import router as calc_router
from views.item_views import router as item_router
from views.model_views import router as model_router
from views.other_views import router as other_views_router
from views.security_views import router as security_router
from views.sotem_views import router as sotem_router
from views.totem_views import router as totem_router


# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])  # add path dependencies for all routes
def create_app(
    debug: bool,
) -> FastAPI:
    app = FastAPI(
        title='FastAPI learning',
        debug=debug,
        version=__version__,
        root_path="/api/v1",
        middleware=middlewares,  # type: ignore[arg-type]
        # openapi_url='/api/v1/openapi.json',
    )

    app.include_router(user_router, tags=["users"])
    app.include_router(model_router, tags=["models"])
    app.include_router(calc_router, tags=["calc"])
    app.include_router(item_router, prefix="/items", tags=["items"])
    app.include_router(totem_router, tags=["totems"])
    app.include_router(sotem_router, tags=["sotems"])
    app.include_router(security_router, tags=["security"])
    app.include_router(background_tasks_router, tags=["background_tasks"])
    app.include_router(other_views_router, tags=["others"])

    # @app.exception_handler(StarletteHTTPException)
    # async def http_exception_handler(request, exc):
    #     return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
    #
    #
    # @app.exception_handler(RequestValidationError)
    # async def validation_exception_handler(request, exc):
    #     return PlainTextResponse(str(exc), status_code=400)

    app.exception_handler(StarletteHTTPException)(exceptions.custom_http_exception_handler)
    app.exception_handler(RequestValidationError)(exceptions.validation_exception_handler)
    app.exception_handler(RequestValidationError)(exceptions.validation_exception_handler2)
    app.exception_handler(exceptions.UnicornError)(exceptions.unicorn_exception_handler)

    return app


def main() -> FastAPI:
    env_settings: AppEnvSettings = AppEnvSettings()
    app = create_app(
        debug=env_settings.FASTAPI_DEBUG,
    )
    DBModel.metadata.create_all(engine)
    return app
