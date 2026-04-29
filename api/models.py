import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(512))
    file_type: Mapped[str] = mapped_column(String(10))
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    page_count: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default='PENDIENTE')
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    opinions: Mapped[list['Opinion']] = relationship(
        back_populates='document', cascade='all, delete-orphan'
    )


class Opinion(Base):
    __tablename__ = 'opinions'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey('documents.id'))
    text: Mapped[str] = mapped_column(Text)
    sentiment: Mapped[str] = mapped_column(String(10))
    confidence: Mapped[float] = mapped_column(Float)
    position: Mapped[int] = mapped_column(Integer)

    document: Mapped['Document'] = relationship(back_populates='opinions')
