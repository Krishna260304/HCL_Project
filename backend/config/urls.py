from django.urls import path
from core.health import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('api/health/', HealthCheckView.as_view(), name='api_health_check'),
]
