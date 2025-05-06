import redis  # type: ignore[import-untyped]
from env_settings import AppEnvSettings
from redis import Redis
from redis import asyncio as aioredis
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


env_settings: AppEnvSettings = AppEnvSettings()
engine = create_engine(str(env_settings.POSTGRES_DSN))

Session = sessionmaker(autoflush=False, bind=engine)


class DBModel(DeclarativeBase):
    pass


class PlaneTotemDB(DBModel):
    __tablename__ = "plane_totem"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa A003
    name: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[float]
    tax: Mapped[float]
    # tags: Mapped[list[str]]


sync_redis = redis.Redis(
    host="redis",
    port=6379,
    db=0,
    decode_responses=True,  # Автоматическое декодирование в строки
)


async def get_aioredis() -> Redis:
    return await aioredis.from_url("redis://redis:6379")
