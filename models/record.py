from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any


@dataclass
class DataRecord:
    """Standardized schema representation for multi-source web scraped data."""
    source: str
    source_url: str
    name_or_title: str
    category: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[int] = None
    author: Optional[str] = None
    tags: Optional[str] = None
    description: Optional[str] = None
    scraped_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert DataRecord instance to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataRecord":
        """Instantiate DataRecord from dictionary."""
        return cls(
            source=data.get("source", ""),
            source_url=data.get("source_url", ""),
            name_or_title=data.get("name_or_title", ""),
            category=data.get("category"),
            price=data.get("price"),
            rating=data.get("rating"),
            author=data.get("author"),
            tags=data.get("tags"),
            description=data.get("description"),
            scraped_at=data.get("scraped_at", datetime.now(timezone.utc).isoformat()),
        )
