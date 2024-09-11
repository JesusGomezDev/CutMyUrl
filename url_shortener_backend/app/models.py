from typing import List
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Urls(Base):
    __tablename__ = 'urls'
    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column()
    original_code: Mapped[str] = mapped_column()
    created_at: Mapped[str] = mapped_column()
    user_id: Mapped[Optional[str]] = mapped_column()

    def __repr__(self) -> str:
        return f"Urls(id={self.id!r}, short_code={self.short_code!r}, original_code={self.original_code!r}, created_at={self.created_at!r}, user_id={self.user_id!r})"