"""
Visitor Management API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..database import db
from ..services.visitor_service import VisitorService
from ..services.pass_service import PassService
from ..models.visitor import Visitor

router = APIRouter(
    prefix="/visitors",
    tags=["visitors"]
)

# Initialize services
visitor_service = VisitorService(db['visitors'])
pass_service = PassService(db['passes'])


@router.post("/register", response_model=Dict[str, Any])
def register_visitor(visitor: Visitor):
    """
    Register a new visitor in the system
    
    This endpoint allows registration of new visitors with either
    blank passes (temporary) or long-term passes.
    """
    try:
        # Validate pass exists and is available
        pass_validation = pass_service.validate_pass(visitor.pass_id)
        if not pass_validation.get("valid"):
            raise HTTPException(
                status_code=400,
                detail=f"Pass validation failed: {pass_validation.get('reason')}"
            )
        
        # Check if pass is available
        pass_doc = pass_service.get_pass(visitor.pass_id)
        if pass_doc and pass_doc.get("is_assigned"):
            raise HTTPException(
                status_code=400,
                detail=f"Pass {visitor.pass_id} is already assigned"
            )
        
        # Create visitor
        visitor_data = visitor.model_dump(exclude_none=True)
        created_visitor = visitor_service.create_visitor(visitor_data)
        
        # Assign pass to visitor
        pass_service.assign_pass(visitor.pass_id, created_visitor["visitor_id"])
        
        return {
            "message": "Visitor registered successfully",
            "visitor": created_visitor
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_visitors(
    active_only: bool = Query(False, description="Return only active (on-premises) visitors"),
    search: Optional[str] = Query(None, description="Search term for name, email, or company")
):
    """
    Get all visitors or search for specific visitors
    """
    try:
        if search:
            visitors = visitor_service.search_visitors(search)
        else:
            visitors = visitor_service.get_all_visitors(active_only=active_only)
        
        # Remove MongoDB _id field and convert datetime to string
        for visitor in visitors:
            if '_id' in visitor:
                del visitor['_id']
            if 'created_at' in visitor and visitor['created_at']:
                visitor['created_at'] = visitor['created_at'].isoformat()
            if 'updated_at' in visitor and visitor['updated_at']:
                visitor['updated_at'] = visitor['updated_at'].isoformat()
        
        return visitors
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{visitor_id}", response_model=Dict[str, Any])
def get_visitor(visitor_id: str):
    """
    Get visitor details by ID
    """
    try:
        visitor = visitor_service.get_visitor(visitor_id)
        if not visitor:
            raise HTTPException(status_code=404, detail=f"Visitor {visitor_id} not found")
        
        # Clean up response
        if '_id' in visitor:
            del visitor['_id']
        if 'created_at' in visitor and visitor['created_at']:
            visitor['created_at'] = visitor['created_at'].isoformat()
        if 'updated_at' in visitor and visitor['updated_at']:
            visitor['updated_at'] = visitor['updated_at'].isoformat()
        
        return visitor
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{visitor_id}", response_model=Dict[str, Any])
def update_visitor(visitor_id: str, update_data: Dict[str, Any]):
    """
    Update visitor information
    """
    try:
        # Check visitor exists
        visitor = visitor_service.get_visitor(visitor_id)
        if not visitor:
            raise HTTPException(status_code=404, detail=f"Visitor {visitor_id} not found")
        
        # Update visitor
        success = visitor_service.update_visitor(visitor_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update visitor")
        
        return {
            "message": "Visitor updated successfully",
            "visitor_id": visitor_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{visitor_id}", response_model=Dict[str, Any])
def delete_visitor(visitor_id: str):
    """
    Delete a visitor from the system
    """
    try:
        # Check visitor exists
        visitor = visitor_service.get_visitor(visitor_id)
        if not visitor:
            raise HTTPException(status_code=404, detail=f"Visitor {visitor_id} not found")
        
        # Unassign pass if assigned
        if visitor.get("pass_id"):
            pass_service.unassign_pass(visitor["pass_id"])
        
        # Delete visitor
        success = visitor_service.delete_visitor(visitor_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete visitor")
        
        return {
            "message": "Visitor deleted successfully",
            "visitor_id": visitor_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/pass/{pass_id}", response_model=Dict[str, Any])
def get_visitor_by_pass(pass_id: str):
    """
    Get visitor by pass ID (NFC or QR code)
    """
    try:
        visitor = visitor_service.get_visitor_by_pass(pass_id)
        if not visitor:
            raise HTTPException(status_code=404, detail=f"No visitor found for pass {pass_id}")
        
        # Clean up response
        if '_id' in visitor:
            del visitor['_id']
        if 'created_at' in visitor and visitor['created_at']:
            visitor['created_at'] = visitor['created_at'].isoformat()
        if 'updated_at' in visitor and visitor['updated_at']:
            visitor['updated_at'] = visitor['updated_at'].isoformat()
        
        return visitor
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
