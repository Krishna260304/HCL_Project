from typing import Any, Dict, List, Set

class SkillGraphEngine:
    @staticmethod
    def build_adjacency_list(skills: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        adj: Dict[str, List[str]] = {str(s['_id']): [] for s in skills if '_id' in s}
        for rel in relationships:
            source = str(rel.get('source_skill_id'))
            target = str(rel.get('target_skill_id'))
            if source in adj:
                adj[source].append(target)
            else:
                adj[source] = [target]
        return adj

    @classmethod
    def get_prerequisites_transitive(cls, skill_id: str, relationships: List[Dict[str, Any]]) -> List[str]:
        target_to_sources: Dict[str, List[str]] = {}
        for rel in relationships:
            if rel.get('relationship_type') == 'prerequisite':
                target = str(rel.get('target_skill_id'))
                source = str(rel.get('source_skill_id'))
                if target not in target_to_sources:
                    target_to_sources[target] = []
                target_to_sources[target].append(source)

        visited: Set[str] = set()
        queue = [skill_id]
        while queue:
            current = queue.pop(0)
            for prereq in target_to_sources.get(current, []):
                if prereq not in visited:
                    visited.add(prereq)
                    queue.append(prereq)
        return list(visited)

    @classmethod
    def get_dependents_transitive(cls, skill_id: str, relationships: List[Dict[str, Any]]) -> List[str]:
        source_to_targets: Dict[str, List[str]] = {}
        for rel in relationships:
            if rel.get('relationship_type') == 'prerequisite':
                source = str(rel.get('source_skill_id'))
                target = str(rel.get('target_skill_id'))
                if source not in source_to_targets:
                    source_to_targets[source] = []
                source_to_targets[source].append(target)

        visited: Set[str] = set()
        queue = [skill_id]
        while queue:
            current = queue.pop(0)
            for dep in source_to_targets.get(current, []):
                if dep not in visited:
                    visited.add(dep)
                    queue.append(dep)
        return list(visited)
