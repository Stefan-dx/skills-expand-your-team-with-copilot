"""
Check-In/Out API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional, List

from ..database import db
from ..services.visitor_service import VisitorService
from ..services.checkinout_service import CheckInOutService
from ..services.cloud_sync_service import CloudSyncService

router = APIRouter(
    prefix="/checkinout",
    tags=["checkinout"]
)

# Initialize services
visitor_service = VisitorService(db['visitors'])
checkinout_service = CheckInOutService(db['checkinout'], visitor_service)
cloud_sync_service = CloudSyncService()


@router.post("/checkin", response_model=Dict[str, Any])
def check_in(
    pass_id: str = Body(..., description="Pass ID for check-in"),
    method: str = Body(..., description="Method used: 'nfc' or 'qr'"),
    location: Optional[str] = Body(None, description="Location identifier"),
    notes: Optional[str] = Body(None, description="Additional notes")
):
    """
    Check in a visitor using their pass (NFC or QR code)
    
    This endpoint records visitor entry and updates the cloud sync file
    for fire department compliance.
    """
    try:
        # Perform check-in
        record = checkinout_service.check_in(pass_id, method, location, notes)
        
        # Generate and sync presence report
        presence_report = checkinout_service.generate_presence_report()
        cloud_sync_service.sync_presence_data(presence_report)
        
        # Clean up response
        if '_id' in record:
            del record['_id']
        if 'timestamp' in record and record['timestamp']:
            record['timestamp'] = record['timestamp'].isoformat()
        
        return {
            "message": "Checked in successfully",
            "record": record,
            "total_present": presence_report.get("total_present", 0)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/checkout", response_model=Dict[str, Any])
def check_out(
    pass_id: str = Body(..., description="Pass ID for check-out"),
    method: str = Body(..., description="Method used: 'nfc' or 'qr'"),
    location: Optional[str] = Body(None, description="Location identifier"),
    notes: Optional[str] = Body(None, description="Additional notes")
):
    """
    Check out a visitor using their pass (NFC or QR code)
    
    This endpoint records visitor exit and updates the cloud sync file
    for fire department compliance.
    """
    try:
        # Perform check-out
        record = checkinout_service.check_out(pass_id, method, location, notes)
        
        # Generate and sync presence report
        presence_report = checkinout_service.generate_presence_report()
        cloud_sync_service.sync_presence_data(presence_report)
        
        # Clean up response
        if '_id' in record:
            del record['_id']
        if 'timestamp' in record and record['timestamp']:
            record['timestamp'] = record['timestamp'].isoformat()
        
        return {
            "message": "Checked out successfully",
            "record": record,
            "total_present": presence_report.get("total_present", 0)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/present", response_model=List[Dict[str, Any]])
def get_present_visitors():
    """
    Get list of all visitors currently on premises
    """
    try:
        visitors = checkinout_service.get_currently_present()
        
        # Clean up response
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


@router.get("/present/count", response_model=Dict[str, int])
def get_present_count():
    """
    Get count of visitors currently on premises
    """
    try:
        count = checkinout_service.get_present_count()
        return {"count": count}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/history/{visitor_id}", response_model=List[Dict[str, Any]])
def get_visitor_history(
    visitor_id: str,
    days: Optional[int] = Query(None, description="Number of days to look back")
):
    """
    Get check-in/out history for a specific visitor
    """
    try:
        records = checkinout_service.get_visitor_history(visitor_id, days)
        
        # Clean up response
        for record in records:
            if '_id' in record:
                del record['_id']
            if 'timestamp' in record and record['timestamp']:
                record['timestamp'] = record['timestamp'].isoformat()
        
        return records
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/history", response_model=List[Dict[str, Any]])
def get_all_history(
    days: Optional[int] = Query(None, description="Number of days to look back")
):
    """
    Get all check-in/out records
    """
    try:
        records = checkinout_service.get_all_records(days)
        
        # Clean up response
        for record in records:
            if '_id' in record:
                del record['_id']
            if 'timestamp' in record and record['timestamp']:
                record['timestamp'] = record['timestamp'].isoformat()
        
        return records
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/report/presence", response_model=Dict[str, Any])
def get_presence_report():
    """
    Generate current visitor presence report
    
    This report is used for fire department building evacuation compliance.
    """
    try:
        report = checkinout_service.generate_presence_report()
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sync/status", response_model=Dict[str, Any])
def get_sync_status():
    """
    Get cloud sync status and last sync time
    """
    try:
        verification = cloud_sync_service.verify_sync()
        return {
            "last_sync": cloud_sync_service.get_last_sync_time(),
            "verification": verification
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/sync/data", response_model=Dict[str, Any])
def get_synced_data():
    """
    Get current synced presence data from cloud
    """
    try:
        data = cloud_sync_service.get_synced_data()
        return data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
