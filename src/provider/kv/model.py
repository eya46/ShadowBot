from sqlalchemy.orm import Mapped, mapped_column

from nonebot_plugin_orm import Model


class KV(Model):
    __tablename__ = "kv"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]


if __name__ == '__main__' or True:
    from sqlalchemy.schema import CreateTable
    from nonebot import logger

    logger.debug(CreateTable(KV.__table__))
