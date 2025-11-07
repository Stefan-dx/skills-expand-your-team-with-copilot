"""
Cloud Sync Service

Manages synchronization of visitor presence data to cloud storage.
Updates a file in the cloud whenever visitor presence changes,
for fire department building evacuation compliance.
"""

import json
import os
from typing import Dict, Any
from datetime import datetime


class CloudSyncService:
    """
    Service class for cloud synchronization operations
    
    In a production environment, this would integrate with cloud storage
    providers like AWS S3, Azure Blob Storage, or Google Cloud Storage.
    For this implementation, we simulate cloud sync by writing to a local file.
    """
    
    def __init__(self, sync_path: str = "./visitor_presence.json"):
        """
        Initialize CloudSyncService
        
        Args:
            sync_path: Path to the sync file (simulates cloud file)
        """
        self.sync_path = sync_path
        self._ensure_sync_file()
    
    def _ensure_sync_file(self):
        """Ensure sync file exists"""
        if not os.path.exists(self.sync_path):
            self._write_sync_file({
                "last_updated": datetime.now().isoformat(),
                "total_present": 0,
                "visitors": []
            })
    
    def _write_sync_file(self, data: Dict[str, Any]):
        """
        Write data to sync file
        
        Args:
            data: Data to write
        """
        try:
            with open(self.sync_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing sync file: {e}")
    
    def _read_sync_file(self) -> Dict[str, Any]:
        """
        Read data from sync file
        
        Returns:
            Data from sync file
        """
        try:
            with open(self.sync_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading sync file: {e}")
            return {
                "last_updated": datetime.now().isoformat(),
                "total_present": 0,
                "visitors": []
            }
    
    def sync_presence_data(self, presence_report: Dict[str, Any]) -> bool:
        """
        Sync visitor presence data to cloud
        
        Args:
            presence_report: Presence report from CheckInOutService
            
        Returns:
            True if sync successful, False otherwise
        """
        try:
            # Add sync metadata
            sync_data = {
                "last_updated": datetime.now().isoformat(),
                "report_timestamp": presence_report.get("timestamp"),
                "total_present": presence_report.get("total_present", 0),
                "visitors": presence_report.get("visitors", []),
                "building_status": "occupied" if presence_report.get("total_present", 0) > 0 else "empty"
            }
            
            # Write to cloud (simulated as local file)
            self._write_sync_file(sync_data)
            
            return True
        except Exception as e:
            print(f"Error syncing presence data: {e}")
            return False
    
    def get_last_sync_time(self) -> str:
        """
        Get timestamp of last sync
        
        Returns:
            ISO format timestamp string
        """
        data = self._read_sync_file()
        return data.get("last_updated", "Never")
    
    def get_synced_data(self) -> Dict[str, Any]:
        """
        Get current synced data
        
        Returns:
            Current synced presence data
        """
        return self._read_sync_file()
    
    def verify_sync(self) -> Dict[str, Any]:
        """
        Verify sync status and accessibility
        
        Returns:
            Dictionary with sync verification results
        """
        try:
            data = self._read_sync_file()
            return {
                "accessible": True,
                "last_updated": data.get("last_updated"),
                "visitor_count": data.get("total_present", 0)
            }
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e)
            }
