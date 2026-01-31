from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel

DataT = TypeVar("DataT")

class ResponseWrapper(BaseModel, Generic[DataT]):
    data: DataT
    confidence: float = 1.0
    reasoning: Optional[str] = None
    warnings: List[str] = []

class AIResponse(BaseModel):
    confidence: float
    reasoning: str
    stage: str
    metadata: Optional[Any] = None
