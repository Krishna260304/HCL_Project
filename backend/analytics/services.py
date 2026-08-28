from typing import Any, Dict, Optional
from core.permissions import require_admin
from analytics.repository import AnalyticsRepository

class AnalyticsService:
    @classmethod
    def get_overview(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        return AnalyticsRepository.get_overview_metrics()
