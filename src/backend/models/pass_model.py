"""
Pass Model

Represents a visitor pass (NFC or QR code) in the system.
Supports both blank passes (for temporary registration) and 
long-term passes (for regular visitors).
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Pass(BaseModel):
    """
    Pass data model
    
    Attributes:
        pass_id: Unique pass identifier (NFC chip ID or QR code)
        pass_type: Type of pass ('blank' or 'longterm')
        nfc_id: NFC chip identifier (if applicable)
        qr_code: QR code value (if applicable)
        is_assigned: Whether the pass is currently assigned to a visitor
        assigned_to: Visitor ID if assigned
        valid_from: Start date of pass validity
        valid_until: End date of pass validity (None for unlimited)
        is_active: Whether the pass is currently active
        created_at: Timestamp of pass creation
        updated_at: Timestamp of last update
    """
    pass_id: str = Field(..., description="Unique pass identifier")
    pass_type: str = Field(..., description="Pass type: 'blank' or 'longterm'")
    nfc_id: Optional[str] = Field(None, description="NFC chip identifier")
    qr_code: Optional[str] = Field(None, description="QR code value")
    is_assigned: bool = Field(default=False, description="Pass is assigned to a visitor")
    assigned_to: Optional[str] = Field(None, description="Visitor ID if assigned")
    valid_from: Optional[datetime] = Field(None, description="Pass validity start date")
    valid_until: Optional[datetime] = Field(None, description="Pass validity end date")
    is_active: bool = Field(default=True, description="Pass is currently active")
    created_at: Optional[datetime] = Field(None, description="Pass creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "pass_id": "NFC-12345678",
                "pass_type": "longterm",
                "nfc_id": "04:5E:A2:3A:1B:80",
                "qr_code": "VIS-LT-12345678",
                "is_assigned": True,
                "assigned_to": "visitor_001"
            }
        }
