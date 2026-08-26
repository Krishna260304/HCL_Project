from typing import Any, Dict
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import redis
import httpx
from database.mongo import get_client

def check_mongodb_health() -> str:
    try:
        client = get_client()
        client.admin.command('ping')
        return 'ok'
    except Exception:
        return 'unreachable'

def check_redis_health() -> str:
    try:
        redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
        r = redis.Redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        return 'ok'
    except Exception:
        return 'unreachable'

def check_ai_service_health() -> str:
    base_url = getattr(settings, 'AI_SERVICE_BASE_URL', '')
    if not base_url:
        return 'not_configured'
    try:
        response = httpx.get(f'{base_url}/health', timeout=2.0)
        return 'available' if response.status_code == 200 else f'status_{response.status_code}'
    except Exception:
        return 'external_unreachable'

def get_system_health() -> Dict[str, Any]:
    mongo_status = check_mongodb_health()
    redis_status = check_redis_health()
    ai_status = check_ai_service_health()
    is_healthy = (mongo_status == 'ok')
    return {
        'status': 'healthy' if is_healthy else 'degraded',
        'components': {
            'django': 'ok',
            'mongodb': mongo_status,
            'redis': redis_status,
            'ai_service': ai_status,
        }
    }

class HealthCheckView(APIView):
    def get(self, request, *args, **kwargs):
        health_data = get_system_health()
        status_code = status.HTTP_200_OK if health_data['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(health_data, status=status_code)
