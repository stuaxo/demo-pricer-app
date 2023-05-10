from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from pricer_app.config import settings
from pricer_app.market_data.routes import router as market_data_router


def create_app(db_url: str = None) -> FastAPI:
    if db_url is None:
        db_url = settings.db_url

    if db_url is None:
        raise ValueError("db_url must be provided")

    app = FastAPI()

    app.include_router(market_data_router)

    register_tortoise(
        app,
        db_url=db_url,
        config={
            "connections": {"default": db_url},
        },
        modules={
            "models": ["pricer_app.market_data.models"],
        },
        generate_schemas=True,
        add_exception_handlers=True,
    )

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
