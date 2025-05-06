from env_settings import AppEnvSettings
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
