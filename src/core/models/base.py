from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa
