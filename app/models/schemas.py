from pydantic import BaseModel, ConfigDict
from typing import List, Union
from datetime import datetime
from bson import ObjectId

class SummaryItem(BaseModel):
    filename: str
    summary: Union[str, None] = None
    error: Union[str, None] = None

class BaseSummaryResponse(BaseModel):
    request_id: str
    user_id: str
    timestamp: datetime
    summaries: List[SummaryItem]
    record_id: str

    model_config = ConfigDict(
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        },
        arbitrary_types_allowed=True
    )

class FullAnalysisResponse(BaseModel):
    request_id: str
    user_id: str
    timestamp: datetime
    summaries: List[SummaryItem]
    best_candidate_answer: str
    record_id: str

    model_config = ConfigDict(
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        },
        arbitrary_types_allowed=True
    )

class SummariesOnlyResponse(BaseModel):
    request_id: str
    user_id: str
    timestamp: datetime
    summaries: List[SummaryItem]
    record_id: str

    model_config = ConfigDict(
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        },
        arbitrary_types_allowed=True
    )
