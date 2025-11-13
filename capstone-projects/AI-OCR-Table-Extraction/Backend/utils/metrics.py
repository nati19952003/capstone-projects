from datetime import datetime
from typing import Optional, List, Dict
from ..database.models import SystemMetric
from ..database.database import Database

class MetricsService:
    def __init__(self, db: Database):
        self.db = db

    async def record_metric(
        self,
        metric_name: str,
        metric_value: float,
        tags: Optional[Dict] = None
    ):
        metric = SystemMetric(
            metric_name=metric_name,
            metric_value=metric_value,
            tags=tags or {}
        )
        await self.db.system_metrics.insert_one(metric.to_dict())

    async def get_metrics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        tags: Optional[Dict] = None
    ) -> List[Dict]:
        query = {
            "metric_name": metric_name,
            "recorded_at": {
                "$gte": start_time,
                "$lte": end_time
            }
        }
        
        if tags:
            for key, value in tags.items():
                query[f"tags.{key}"] = value
                
        cursor = self.db.system_metrics.find(query).sort("recorded_at", 1)
        return await cursor.to_list(length=None)

    async def get_latest_metric(
        self,
        metric_name: str,
        tags: Optional[Dict] = None
    ) -> Optional[Dict]:
        query = {"metric_name": metric_name}
        
        if tags:
            for key, value in tags.items():
                query[f"tags.{key}"] = value
                
        result = await self.db.system_metrics.find_one(
            query,
            sort=[("recorded_at", -1)]
        )
        return result

    async def calculate_metric_stats(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        tags: Optional[Dict] = None
    ) -> Dict:
        pipeline = [
            {
                "$match": {
                    "metric_name": metric_name,
                    "recorded_at": {
                        "$gte": start_time,
                        "$lte": end_time
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg": {"$avg": "$metric_value"},
                    "min": {"$min": "$metric_value"},
                    "max": {"$max": "$metric_value"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        if tags:
            for key, value in tags.items():
                pipeline[0]["$match"][f"tags.{key}"] = value
                
        results = await self.db.system_metrics.aggregate(pipeline).to_list(length=1)
        return results[0] if results else {
            "avg": 0,
            "min": 0,
            "max": 0,
            "count": 0
        }