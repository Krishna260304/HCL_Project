from typing import Any, Dict
from core.validators import validate_required_fields

def validate_external_search_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['query'])
    return {
        'provider': str(data.get('provider', 'youtube')).strip().lower(),
        'query': str(data['query']).strip(),
        'max_results': max(1, min(50, int(data.get('max_results', 10)))),
    }
