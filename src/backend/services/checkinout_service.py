"""
Check-In/Out Service

Business logic for managing visitor check-ins and check-outs.
Tracks visitor presence and generates compliance reports.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid


class CheckInOutService:
    """
    Service class for check-in/out operations
    """
    
    def __init__(self, checkinout_collection, visitor_service):
        """
        Initialize CheckInOutService
        
        Args:
            checkinout_collection: MongoDB collection for check-in/out records
            visitor_service: VisitorService instance
        """
        self.checkinout_collection = checkinout_collection
        self.visitor_service = visitor_service
    
    def check_in(self, pass_id: str, method: str, location: Optional[str] = None, 
                 notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Check in a visitor
        
        Args:
            pass_id: Pass identifier used for check-in
            method: Method used ('nfc' or 'qr')
            location: Optional location identifier
            notes: Optional notes
            
        Returns:
            Check-in record
            
        Raises:
            ValueError: If visitor not found or already checked in
        """
        # Get visitor by pass
        visitor = self.visitor_service.get_visitor_by_pass(pass_id)
        if not visitor:
            raise ValueError(f"No visitor found for pass {pass_id}")
        
        visitor_id = visitor["visitor_id"]
        
        # Check if already checked in
        if visitor.get("is_active"):
            raise ValueError(f"Visitor {visitor_id} is already checked in")
        
        # Create check-in record
        record_id = f"record_{uuid.uuid4().hex[:8]}"
        record = {
            "_id": record_id,
            "record_id": record_id,
            "visitor_id": visitor_id,
            "pass_id": pass_id,
            "action": "checkin",
            "timestamp": datetime.now(),
            "method": method,
            "location": location,
            "notes": notes
        }
        
        # Insert record
        self.checkinout_collection.insert_one(record)
        
        # Update visitor status
        self.visitor_service.set_visitor_active_status(visitor_id, True)
        
        return record
    
    def check_out(self, pass_id: str, method: str, location: Optional[str] = None,
                  notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Check out a visitor
        
        Args:
            pass_id: Pass identifier used for check-out
            method: Method used ('nfc' or 'qr')
            location: Optional location identifier
            notes: Optional notes
            
        Returns:
            Check-out record
            
        Raises:
            ValueError: If visitor not found or not checked in
        """
        # Get visitor by pass
        visitor = self.visitor_service.get_visitor_by_pass(pass_id)
        if not visitor:
            raise ValueError(f"No visitor found for pass {pass_id}")
        
        visitor_id = visitor["visitor_id"]
        
        # Check if checked in
        if not visitor.get("is_active"):
            raise ValueError(f"Visitor {visitor_id} is not currently checked in")
        
        # Create check-out record
        record_id = f"record_{uuid.uuid4().hex[:8]}"
        record = {
            "_id": record_id,
            "record_id": record_id,
            "visitor_id": visitor_id,
            "pass_id": pass_id,
            "action": "checkout",
            "timestamp": datetime.now(),
            "method": method,
            "location": location,
            "notes": notes
        }
        
        # Insert record
        self.checkinout_collection.insert_one(record)
        
        # Update visitor status
        self.visitor_service.set_visitor_active_status(visitor_id, False)
        
        return record
    
    def get_visitor_history(self, visitor_id: str, 
                           days: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get check-in/out history for a visitor
        
        Args:
            visitor_id: Visitor identifier
            days: Optional number of days to look back
            
        Returns:
            List of check-in/out records
        """
        query = {"visitor_id": visitor_id}
        
        if days:
            since = datetime.now() - timedelta(days=days)
            query["timestamp"] = {"$gte": since}
        
        records = list(self.checkinout_collection.find(query).sort("timestamp", -1))
        return records
    
    def get_all_records(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all check-in/out records
        
        Args:
            days: Optional number of days to look back
            
        Returns:
            List of check-in/out records
        """
        query = {}
        
        if days:
            since = datetime.now() - timedelta(days=days)
            query["timestamp"] = {"$gte": since}
        
        records = list(self.checkinout_collection.find(query).sort("timestamp", -1))
        return records
    
    def get_currently_present(self) -> List[Dict[str, Any]]:
        """
        Get list of all visitors currently on premises
        
        Returns:
            List of visitor documents for those currently checked in
        """
        return self.visitor_service.get_all_visitors(active_only=True)
    
    def get_present_count(self) -> int:
        """
        Get count of visitors currently on premises
        
        Returns:
            Number of visitors currently checked in
        """
        return len(self.get_currently_present())
    
    def generate_presence_report(self) -> Dict[str, Any]:
        """
        Generate a report of current visitor presence
        For fire department compliance
        
        Returns:
            Dictionary with presence information
        """
        present_visitors = self.get_currently_present()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_present": len(present_visitors),
            "visitors": []
        }
        
        for visitor in present_visitors:
            # Get last check-in time
            last_checkin = self.checkinout_collection.find_one(
                {
                    "visitor_id": visitor["visitor_id"],
                    "action": "checkin"
                },
                sort=[("timestamp", -1)]
            )
            
            report["visitors"].append({
                "visitor_id": visitor["visitor_id"],
                "name": f"{visitor.get('first_name', '')} {visitor.get('last_name', '')}",
                "email": visitor.get("email", ""),
                "company": visitor.get("company", ""),
                "pass_id": visitor.get("pass_id", ""),
                "checked_in_at": last_checkin["timestamp"].isoformat() if last_checkin else None
            })
        
        return report
