from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class Attachment(BaseModel):
    """Represents a Genie response attachment"""
    type: str  # "text", "query", "error"
    content: Dict[str, Any]
    attachment_id: Optional[str] = None

class GenieResponse(BaseModel):
    """Comprehensive response model for Genie operations"""
    success: bool
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    status: str  # IN_PROGRESS, EXECUTING_QUERY, COMPLETED, FAILED, CANCELLED
    attachments: List[Attachment] = []
    results: Optional[Dict[str, Any]] = None
    natural_language_answer: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = {}  # For usage tracking
    
    def finalize(self):
        """Finalizes response with end time and duration"""
        self.end_time = datetime.now()
        if self.start_time and self.end_time:
            self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000