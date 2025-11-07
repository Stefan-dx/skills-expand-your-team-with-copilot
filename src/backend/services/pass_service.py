"""
Pass Service

Business logic for managing visitor passes (NFC and QR codes).
Handles pass creation, assignment, and validation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class PassService:
    """
    Service class for pass management operations
    """
    
    def __init__(self, passes_collection):
        """
        Initialize PassService
        
        Args:
            passes_collection: MongoDB collection for passes
        """
        self.passes_collection = passes_collection
    
    def create_pass(self, pass_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new pass in the system
        
        Args:
            pass_data: Dictionary containing pass information
            
        Returns:
            Created pass document
            
        Raises:
            ValueError: If pass with same ID already exists
        """
        # Check if pass already exists
        existing = self.passes_collection.find_one({"_id": pass_data.get("pass_id")})
        if existing:
            raise ValueError(f"Pass {pass_data.get('pass_id')} already exists")
        
        # Add metadata
        pass_data["_id"] = pass_data["pass_id"]
        pass_data["is_assigned"] = False
        pass_data["is_active"] = True
        pass_data["created_at"] = datetime.now()
        pass_data["updated_at"] = datetime.now()
        
        # Insert into database
        self.passes_collection.insert_one(pass_data)
        
        return pass_data
    
    def get_pass(self, pass_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pass by ID
        
        Args:
            pass_id: Pass identifier
            
        Returns:
            Pass document or None if not found
        """
        pass_doc = self.passes_collection.find_one({"_id": pass_id})
        return pass_doc
    
    def get_pass_by_nfc(self, nfc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pass by NFC ID
        
        Args:
            nfc_id: NFC chip identifier
            
        Returns:
            Pass document or None if not found
        """
        pass_doc = self.passes_collection.find_one({"nfc_id": nfc_id})
        return pass_doc
    
    def get_pass_by_qr(self, qr_code: str) -> Optional[Dict[str, Any]]:
        """
        Get pass by QR code
        
        Args:
            qr_code: QR code value
            
        Returns:
            Pass document or None if not found
        """
        pass_doc = self.passes_collection.find_one({"qr_code": qr_code})
        return pass_doc
    
    def get_available_passes(self, pass_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all available (unassigned) passes
        
        Args:
            pass_type: Optional filter by pass type ('blank' or 'longterm')
            
        Returns:
            List of available pass documents
        """
        query = {
            "is_assigned": False,
            "is_active": True
        }
        
        if pass_type:
            query["pass_type"] = pass_type
        
        passes = list(self.passes_collection.find(query))
        return passes
    
    def assign_pass(self, pass_id: str, visitor_id: str) -> bool:
        """
        Assign a pass to a visitor
        
        Args:
            pass_id: Pass identifier
            visitor_id: Visitor identifier
            
        Returns:
            True if assigned successfully, False otherwise
            
        Raises:
            ValueError: If pass is already assigned or not found
        """
        # Check if pass exists and is available
        pass_doc = self.get_pass(pass_id)
        if not pass_doc:
            raise ValueError(f"Pass {pass_id} not found")
        
        if pass_doc.get("is_assigned"):
            raise ValueError(f"Pass {pass_id} is already assigned")
        
        # Assign pass
        result = self.passes_collection.update_one(
            {"_id": pass_id},
            {
                "$set": {
                    "is_assigned": True,
                    "assigned_to": visitor_id,
                    "updated_at": datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    
    def unassign_pass(self, pass_id: str) -> bool:
        """
        Unassign a pass from a visitor
        
        Args:
            pass_id: Pass identifier
            
        Returns:
            True if unassigned successfully, False otherwise
        """
        result = self.passes_collection.update_one(
            {"_id": pass_id},
            {
                "$set": {
                    "is_assigned": False,
                    "assigned_to": None,
                    "updated_at": datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    
    def validate_pass(self, pass_id: str) -> Dict[str, Any]:
        """
        Validate if a pass is active and can be used
        
        Args:
            pass_id: Pass identifier
            
        Returns:
            Dictionary with validation result
        """
        pass_doc = self.get_pass(pass_id)
        
        if not pass_doc:
            return {"valid": False, "reason": "Pass not found"}
        
        if not pass_doc.get("is_active"):
            return {"valid": False, "reason": "Pass is inactive"}
        
        # Check validity period if set
        valid_until = pass_doc.get("valid_until")
        if valid_until and datetime.now() > valid_until:
            return {"valid": False, "reason": "Pass has expired"}
        
        valid_from = pass_doc.get("valid_from")
        if valid_from and datetime.now() < valid_from:
            return {"valid": False, "reason": "Pass is not yet valid"}
        
        return {"valid": True, "pass": pass_doc}
    
    def deactivate_pass(self, pass_id: str) -> bool:
        """
        Deactivate a pass
        
        Args:
            pass_id: Pass identifier
            
        Returns:
            True if deactivated successfully, False otherwise
        """
        result = self.passes_collection.update_one(
            {"_id": pass_id},
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
