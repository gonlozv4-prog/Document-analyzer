from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DocumentMetadata:
    filename: str
    file_path: str
    file_type: str  # 'pdf' | 'tiff'
    file_size_bytes: int
    page_count: int
    user_id: str
    upload_date: datetime = field(default_factory=datetime.utcnow)
