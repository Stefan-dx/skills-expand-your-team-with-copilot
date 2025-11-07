"""
Check-In/Out Model

Represents a check-in or check-out event in the visitor management system.
Used to track visitor presence for compliance and security purposes.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CheckInOut(BaseModel):
    """
    Check-In/Out data model
    
    Attributes:
        record_id: Unique record identifier (auto-generated)
        visitor_id: ID of the visitor
        pass_id: Pass used for check-in/out
        action: Type of action ('checkin' or 'checkout')
        timestamp: Time of the action
        method: Method used ('nfc' or 'qr')
        location: Optional location identifier
        notes: Optional notes about the visit
    """
    record_id: Optional[str] = Field(None, description="Unique record identifier")
    visitor_id: str = Field(..., description="Visitor identifier")
    pass_id: str = Field(..., description="Pass identifier used")
    action: str = Field(..., description="Action type: 'checkin' or 'checkout'")
    timestamp: datetime = Field(default_factory=datetime.now, description="Action timestamp")
    method: str = Field(..., description="Method used: 'nfc' or 'qr'")
    location: Optional[str] = Field(None, description="Location identifier")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "visitor_id": "visitor_001",
                "pass_id": "NFC-12345678",
                "action": "checkin",
                "method": "nfc",
                "location": "Main Entrance"
            }
        }
