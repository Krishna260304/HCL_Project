from typing import Any, Dict, List
from core.constants import ResourceType, ResourceStatus

def normalize_resource_data(data: Dict[str, Any]) -> Dict[str, Any]:
    res_type = data.get('type', ResourceType.ARTICLE)
    if res_type not in ResourceType.ALL_TYPES:
        res_type = ResourceType.ARTICLE

    status = data.get('status', ResourceStatus.PUBLISHED)
    if status not in ResourceStatus.ALL_STATUSES:
        status = ResourceStatus.PUBLISHED

    skills = data.get('skills', [])
    if not isinstance(skills, list):
        skills = [skills] if skills else []

    tags = data.get('tags', [])
    if not isinstance(tags, list):
        tags = [tags] if tags else []

    return {
        'title': str(data.get('title', '')).strip(),
        'description': str(data.get('description', '')).strip(),
        'source': str(data.get('source', 'internal')).strip(),
        'source_id': str(data.get('source_id', '')).strip(),
        'url': str(data.get('url', '')).strip(),
        'type': res_type,
        'difficulty': str(data.get('difficulty', 'beginner')).strip(),
        'duration': max(0, int(data.get('duration', 0))),
        'skills': [str(s).strip() for s in skills if s],
        'prerequisites': data.get('prerequisites', []) if isinstance(data.get('prerequisites'), list) else [],
        'quality_score': max(0.0, min(1.0, float(data.get('quality_score', 0.8)))),
        'rating': max(0.0, min(5.0, float(data.get('rating', 0.0)))),
        'tags': [str(t).strip() for t in tags if t],
        'language': str(data.get('language', 'en')).strip(),
        'status': status,
        'metadata': data.get('metadata', {}) if isinstance(data.get('metadata'), dict) else {},
    }
