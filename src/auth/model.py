# src/auth/model.py
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from src.core.base_model import Base, DateTimeMixin

if TYPE_CHECKING: # 只用于静态类型检查，运行时不执行，不会循环导入
    from src.collection.model import Collection

class User(SQLAlchemyBaseUserTableUUID, DateTimeMixin, Base):
    name: Mapped[str] = mapped_column(String(64), nullable=True)

    collections: Mapped[list["Collection"]] = relationship(
        back_populates="user",          # 双向
        cascade="all, delete",          # 关键：User 被删时自动删 collections
        passive_deletes=True,           # 让数据库外键 ON DELETE CASCADE 生效
    )


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass
