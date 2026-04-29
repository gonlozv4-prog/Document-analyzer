from datetime import datetime

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    status: str


class DocumentStatus(BaseModel):
    id: str
    filename: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None


class OpinionResult(BaseModel):
    id: str
    text: str
    sentiment: str
    confidence: float
    position: int


class AnalysisSummary(BaseModel):
    total: int
    positive: int
    negative: int
    positive_pct: float
    negative_pct: float


class DocumentResults(BaseModel):
    id: str
    filename: str
    status: str
    summary: AnalysisSummary
    opinions: list[OpinionResult]
