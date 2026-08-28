from typing import Any, Dict, Optional
import httpx
from ai_integrations.config import AIConfig
from ai_integrations.exceptions import ExternalAIServiceUnavailableError, ExternalAIResponseValidationError

class BaseAIClient:
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {AIConfig.get_api_key()}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    @classmethod
    def post(cls, endpoint: str, payload: Dict[str, Any], timeout: Optional[int] = None) -> Dict[str, Any]:
        url = f"{AIConfig.get_base_url().rstrip('/')}/{endpoint.lstrip('/')}"
        req_timeout = timeout or AIConfig.get_timeout()
        try:
            with httpx.Client(timeout=req_timeout) as client:
                response = client.post(url, json=payload, headers=cls.get_headers())
                if response.status_code >= 400:
                    raise ExternalAIServiceUnavailableError(
                        f"AI service returned HTTP status {response.status_code}",
                        details={'status_code': response.status_code, 'body': response.text}
                    )
                return response.json()
        except httpx.RequestError as exc:
            raise ExternalAIServiceUnavailableError(
                f"Failed to connect to external AI service at {url}: {str(exc)}",
                details={'error': str(exc), 'endpoint': endpoint}
            )
        except ValueError as exc:
            raise ExternalAIResponseValidationError(
                f"Invalid JSON response from AI service: {str(exc)}",
                details={'error': str(exc)}
            )
