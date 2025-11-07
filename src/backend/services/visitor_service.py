"""
Visitor Service

Business logic for managing visitors in the system.
Handles visitor registration, updates, and queries.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class VisitorService:
    """
    Service class for visitor management operations
    """
    
    def __init__(self, visitors_collection):
        """
        Initialize VisitorService
        
        Args:
            visitors_collection: MongoDB collection for visitors
        """
        self.visitors_collection = visitors_collection
    
    def create_visitor(self, visitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new visitor in the system
        
        Args:
            visitor_data: Dictionary containing visitor information
            
        Returns:
            Created visitor document with visitor_id
            
        Raises:
            ValueError: If visitor with same email or pass_id already exists
        """
        # Check if visitor with same email already exists
        existing = self.visitors_collection.find_one({"email": visitor_data.get("email")})
        if existing:
            raise ValueError(f"Visitor with email {visitor_data.get('email')} already exists")
        
        # Check if pass is already assigned
        existing_pass = self.visitors_collection.find_one({"pass_id": visitor_data.get("pass_id")})
        if existing_pass:
            raise ValueError(f"Pass {visitor_data.get('pass_id')} is already assigned")
        
        # Generate unique visitor ID
        visitor_id = f"visitor_{uuid.uuid4().hex[:8]}"
        
        # Add metadata
        visitor_data["_id"] = visitor_id
        visitor_data["visitor_id"] = visitor_id
        visitor_data["is_active"] = False
        visitor_data["created_at"] = datetime.now()
        visitor_data["updated_at"] = datetime.now()
        
        # Insert into database
        self.visitors_collection.insert_one(visitor_data)
        
        return visitor_data
    
    def get_visitor(self, visitor_id: str) -> Optional[Dict[str, Any]]:
        """
        Get visitor by ID
        
        Args:
            visitor_id: Unique visitor identifier
            
        Returns:
            Visitor document or None if not found
        """
        visitor = self.visitors_collection.find_one({"_id": visitor_id})
        return visitor
    
    def get_visitor_by_pass(self, pass_id: str) -> Optional[Dict[str, Any]]:
        """
        Get visitor by pass ID
        
        Args:
            pass_id: Pass identifier
            
        Returns:
            Visitor document or None if not found
        """
        visitor = self.visitors_collection.find_one({"pass_id": pass_id})
        return visitor
    
    def get_all_visitors(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all visitors
        
        Args:
            active_only: If True, return only visitors currently on premises
            
        Returns:
            List of visitor documents
        """
        query = {}
        if active_only:
            query["is_active"] = True
        
        visitors = list(self.visitors_collection.find(query))
        return visitors
    
    def update_visitor(self, visitor_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update visitor information
        
        Args:
            visitor_id: Visitor identifier
            update_data: Dictionary with fields to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        # Add update timestamp
        update_data["updated_at"] = datetime.now()
        
        # Update document
        result = self.visitors_collection.update_one(
            {"_id": visitor_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    def set_visitor_active_status(self, visitor_id: str, is_active: bool) -> bool:
        """
        Set visitor's active status (on/off premises)
        
        Args:
            visitor_id: Visitor identifier
            is_active: Active status to set
            
        Returns:
            True if updated successfully, False otherwise
        """
        return self.update_visitor(visitor_id, {"is_active": is_active})
    
    def delete_visitor(self, visitor_id: str) -> bool:
        """
        Delete a visitor from the system
        
        Args:
            visitor_id: Visitor identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        result = self.visitors_collection.delete_one({"_id": visitor_id})
        return result.deleted_count > 0
    
    def search_visitors(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search visitors by name, email, or company
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching visitor documents
        """
        query = {
            "$or": [
                {"first_name": {"$regex": search_term, "$options": "i"}},
                {"last_name": {"$regex": search_term, "$options": "i"}},
                {"email": {"$regex": search_term, "$options": "i"}},
                {"company": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        visitors = list(self.visitors_collection.find(query))
        return visitors
