from datetime import datetime
from typing import Optional
from ..database.models import AuditLog
from ..database.database import Database

class AuditLogger:
    def __init__(self, db: Database):
        self.db = db

    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[dict] = None
    ):
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        log_dict = log.to_dict()
        if details:
            log_dict["details"] = details
        
        await self.db.audit_logs.insert_one(log_dict)

    async def get_user_actions(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        resource_type: Optional[str] = None,
        limit: int = 100
    ):
        query = {"user_id": user_id}
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["recorded_at"] = date_query
            
        if resource_type:
            query["resource_type"] = resource_type
            
        cursor = self.db.audit_logs.find(query).sort("recorded_at", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100
    ):
        query = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        
        cursor = self.db.audit_logs.find(query).sort("recorded_at", -1).limit(limit)
        return await cursor.to_list(length=limit)