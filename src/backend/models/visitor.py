"""
Visitor Model

Represents a visitor in the system, containing personal information
and associated pass details.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Visitor(BaseModel):
    """
    Visitor data model
    
    Attributes:
        visitor_id: Unique identifier for the visitor (auto-generated)
        first_name: Visitor's first name
        last_name: Visitor's last name
        email: Visitor's email address
        phone: Optional phone number
        company: Optional company name
        pass_id: Associated pass ID (NFC or QR code identifier)
        pass_type: Type of pass ('blank' or 'longterm')
        is_active: Whether the visitor is currently on premises
        created_at: Timestamp of visitor registration
        updated_at: Timestamp of last update
    """
    visitor_id: Optional[str] = Field(None, description="Unique visitor identifier")
    first_name: str = Field(..., min_length=1, description="Visitor's first name")
    last_name: str = Field(..., min_length=1, description="Visitor's last name")
    email: EmailStr = Field(..., description="Visitor's email address")
    phone: Optional[str] = Field(None, description="Visitor's phone number")
    company: Optional[str] = Field(None, description="Visitor's company")
    pass_id: str = Field(..., description="Associated pass ID (NFC/QR)")
    pass_type: str = Field(..., description="Pass type: 'blank' or 'longterm'")
    is_active: bool = Field(default=False, description="Currently on premises")
    created_at: Optional[datetime] = Field(None, description="Registration timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Max",
                "last_name": "Mustermann",
                "email": "max.mustermann@example.com",
                "phone": "+49 123 456789",
                "company": "Example GmbH",
                "pass_id": "NFC-12345678",
                "pass_type": "longterm"
            }
        }
