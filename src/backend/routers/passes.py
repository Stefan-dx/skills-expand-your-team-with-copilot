"""
Pass Management API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List

from ..database import db
from ..services.pass_service import PassService
from ..models.pass_model import Pass

router = APIRouter(
    prefix="/passes",
    tags=["passes"]
)

# Initialize service
pass_service = PassService(db['passes'])


@router.post("/create", response_model=Dict[str, Any])
def create_pass(pass_data: Pass):
    """
    Create a new pass in the system
    
    This endpoint creates new blank or long-term passes with NFC or QR identifiers.
    """
    try:
        created_pass = pass_service.create_pass(pass_data.model_dump(exclude_none=True))
        
        # Clean up response
        if '_id' in created_pass:
            del created_pass['_id']
        if 'created_at' in created_pass and created_pass['created_at']:
            created_pass['created_at'] = created_pass['created_at'].isoformat()
        if 'updated_at' in created_pass and created_pass['updated_at']:
            created_pass['updated_at'] = created_pass['updated_at'].isoformat()
        if 'valid_from' in created_pass and created_pass['valid_from']:
            created_pass['valid_from'] = created_pass['valid_from'].isoformat()
        if 'valid_until' in created_pass and created_pass['valid_until']:
            created_pass['valid_until'] = created_pass['valid_until'].isoformat()
        
        return {
            "message": "Pass created successfully",
            "pass": created_pass
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/available", response_model=List[Dict[str, Any]])
def get_available_passes(
    pass_type: Optional[str] = Query(None, description="Filter by pass type: 'blank' or 'longterm'")
):
    """
    Get all available (unassigned) passes
    """
    try:
        passes = pass_service.get_available_passes(pass_type=pass_type)
        
        # Clean up response
        for pass_doc in passes:
            if '_id' in pass_doc:
                del pass_doc['_id']
            if 'created_at' in pass_doc and pass_doc['created_at']:
                pass_doc['created_at'] = pass_doc['created_at'].isoformat()
            if 'updated_at' in pass_doc and pass_doc['updated_at']:
                pass_doc['updated_at'] = pass_doc['updated_at'].isoformat()
            if 'valid_from' in pass_doc and pass_doc.get('valid_from'):
                pass_doc['valid_from'] = pass_doc['valid_from'].isoformat()
            if 'valid_until' in pass_doc and pass_doc.get('valid_until'):
                pass_doc['valid_until'] = pass_doc['valid_until'].isoformat()
        
        return passes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{pass_id}", response_model=Dict[str, Any])
def get_pass(pass_id: str):
    """
    Get pass details by ID
    """
    try:
        pass_doc = pass_service.get_pass(pass_id)
        if not pass_doc:
            raise HTTPException(status_code=404, detail=f"Pass {pass_id} not found")
        
        # Clean up response
        if '_id' in pass_doc:
            del pass_doc['_id']
        if 'created_at' in pass_doc and pass_doc['created_at']:
            pass_doc['created_at'] = pass_doc['created_at'].isoformat()
        if 'updated_at' in pass_doc and pass_doc['updated_at']:
            pass_doc['updated_at'] = pass_doc['updated_at'].isoformat()
        if 'valid_from' in pass_doc and pass_doc.get('valid_from'):
            pass_doc['valid_from'] = pass_doc['valid_from'].isoformat()
        if 'valid_until' in pass_doc and pass_doc.get('valid_until'):
            pass_doc['valid_until'] = pass_doc['valid_until'].isoformat()
        
        return pass_doc
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/nfc/{nfc_id}", response_model=Dict[str, Any])
def get_pass_by_nfc(nfc_id: str):
    """
    Get pass by NFC chip ID
    """
    try:
        pass_doc = pass_service.get_pass_by_nfc(nfc_id)
        if not pass_doc:
            raise HTTPException(status_code=404, detail=f"No pass found for NFC ID {nfc_id}")
        
        # Clean up response
        if '_id' in pass_doc:
            del pass_doc['_id']
        if 'created_at' in pass_doc and pass_doc['created_at']:
            pass_doc['created_at'] = pass_doc['created_at'].isoformat()
        if 'updated_at' in pass_doc and pass_doc['updated_at']:
            pass_doc['updated_at'] = pass_doc['updated_at'].isoformat()
        
        return pass_doc
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/qr/{qr_code}", response_model=Dict[str, Any])
def get_pass_by_qr(qr_code: str):
    """
    Get pass by QR code
    """
    try:
        pass_doc = pass_service.get_pass_by_qr(qr_code)
        if not pass_doc:
            raise HTTPException(status_code=404, detail=f"No pass found for QR code {qr_code}")
        
        # Clean up response
        if '_id' in pass_doc:
            del pass_doc['_id']
        if 'created_at' in pass_doc and pass_doc['created_at']:
            pass_doc['created_at'] = pass_doc['created_at'].isoformat()
        if 'updated_at' in pass_doc and pass_doc['updated_at']:
            pass_doc['updated_at'] = pass_doc['updated_at'].isoformat()
        
        return pass_doc
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{pass_id}/validate", response_model=Dict[str, Any])
def validate_pass(pass_id: str):
    """
    Validate if a pass is active and can be used
    """
    try:
        validation_result = pass_service.validate_pass(pass_id)
        return validation_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{pass_id}/deactivate", response_model=Dict[str, Any])
def deactivate_pass(pass_id: str):
    """
    Deactivate a pass
    """
    try:
        success = pass_service.deactivate_pass(pass_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Pass {pass_id} not found or already inactive")
        
        return {
            "message": "Pass deactivated successfully",
            "pass_id": pass_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
