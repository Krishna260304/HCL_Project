from typing import Any, Dict, List
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class LearningPathClient:
    endpoint = 'learning-path'

    @classmethod
    def generate_learning_path(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload, timeout=60)
            return cls.normalize_response(raw_response, payload)
        except Exception:
            return cls.fallback_response(payload)

    @classmethod
    def normalize_response(cls, response: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        goal_title = payload.get('goal', payload.get('target_role', 'Skill Acceleration'))
        raw_phases = response.get('phases', [])
        if not raw_phases:
            return cls.fallback_response(payload)

        formatted_phases = []
        for idx, p in enumerate(raw_phases):
            pid = p.get('phase_id') or p.get('id') or f'phase_{idx + 1}'
            formatted_phases.append({
                'id': str(pid),
                'phase_id': str(pid),
                'title': p.get('title', f'Phase {idx + 1}'),
                'description': p.get('description', ''),
                'objective': p.get('objective', p.get('description', '')),
                'order': p.get('order', idx + 1),
                'skills': p.get('skills', []),
                'resources': p.get('resources', []),
                'projects': p.get('projects', []),
                'assessment': p.get('assessment') if isinstance(p.get('assessment'), str) else (p.get('assessment', {}).get('title') if isinstance(p.get('assessment'), dict) else None),
                'assessment_id': p.get('assessment_id') or (p.get('assessment', {}).get('assessment_id') if isinstance(p.get('assessment'), dict) else None),
                'milestone': p.get('milestone', 'Phase milestone reached'),
                'estimated_duration_weeks': p.get('estimated_duration_weeks', 2),
                'estimated_time': f"{p.get('estimated_duration_weeks', 2)} weeks" if isinstance(p.get('estimated_duration_weeks'), (int, float)) else p.get('estimated_time', '2-3 weeks'),
            })

        return {
            'title': response.get('title', f"Learning Path: {goal_title}"),
            'description': response.get('description', 'Structured roadmap generated to reach your target outcome.'),
            'estimated_duration_weeks': response.get('estimated_duration_weeks', 8),
            'phases': formatted_phases,
        }

    @classmethod
    def fallback_response(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        goal_title = payload.get('goal', payload.get('target_role', 'Skill Acceleration'))
        verified = payload.get('verified_skills', [])
        known_skills = [s.get('skill_id', s) if isinstance(s, dict) else str(s) for s in verified] if verified else ['Python', 'Fundamentals']

        return {
            'title': f"Learning Roadmap: {goal_title}",
            'description': 'A tailored, milestone-driven curriculum mapped to your competency profile and career destination.',
            'estimated_duration_weeks': 8,
            'phases': [
                {
                    'id': 'phase_1',
                    'phase_id': 'phase_1',
                    'title': 'Phase 1: Foundations & Environment Setup',
                    'description': 'Consolidate fundamental competencies, modern toolchains, and environment configuration.',
                    'objective': f'Master foundational principles and establish developer toolchain for {goal_title}.',
                    'order': 1,
                    'skills': known_skills[:3] if known_skills else ['Foundations', 'Programming Logic'],
                    'resources': [
                        {
                            'resource_id': 'res_fnd_01',
                            'title': f'{goal_title} Architecture & Workflow Fundamentals',
                            'resource_type': 'video',
                            'duration_minutes': 60,
                            'skills': known_skills[:2],
                            'is_mandatory': True,
                        }
                    ],
                    'projects': [
                        {
                            'project_id': 'proj_fnd_01',
                            'title': 'Foundational Baseline Lab',
                            'description': 'Implement initial end-to-end prototype and benchmark environment.',
                            'difficulty': 'beginner',
                            'estimated_hours': 4,
                            'deliverables': ['GitHub Repository', 'Initial Codebase'],
                        }
                    ],
                    'assessment': 'Foundational Milestone Quiz',
                    'assessment_id': 'asm_fnd_01',
                    'milestone': 'Core competencies established and verified',
                    'estimated_duration_weeks': 2,
                    'estimated_time': '2 weeks',
                },
                {
                    'id': 'phase_2',
                    'phase_id': 'phase_2',
                    'title': 'Phase 2: Core Architecture & Hands-on Implementation',
                    'description': 'Build realistic pipelines, integrate core components, and develop robust testing practices.',
                    'objective': 'Implement production-grade architecture and solve domain-specific engineering challenges.',
                    'order': 2,
                    'skills': ['Architecture Design', 'Data Pipelines', 'Model Integration'],
                    'resources': [
                        {
                            'resource_id': 'res_core_01',
                            'title': 'Applied Engineering & Component Design',
                            'resource_type': 'documentation',
                            'duration_minutes': 90,
                            'skills': ['Architecture Design'],
                            'is_mandatory': True,
                        }
                    ],
                    'projects': [
                        {
                            'project_id': 'proj_core_01',
                            'title': 'Interactive Applied Milestone Project',
                            'description': 'Construct intermediate project with clean modular architecture and unit tests.',
                            'difficulty': 'intermediate',
                            'estimated_hours': 8,
                            'deliverables': ['Modular service', 'Test suite'],
                        }
                    ],
                    'assessment': 'Intermediate Core Assessment',
                    'assessment_id': 'asm_core_02',
                    'milestone': 'Applied architecture validated',
                    'estimated_duration_weeks': 3,
                    'estimated_time': '3 weeks',
                },
                {
                    'id': 'phase_3',
                    'phase_id': 'phase_3',
                    'title': 'Phase 3: Production Deployment & Capstone Portfolio',
                    'description': 'Optimize performance, containerize services, and deploy capstone application to production.',
                    'objective': f'Deliver production-grade capstone project demonstrating end-to-end readiness for {goal_title}.',
                    'order': 3,
                    'skills': ['Deployment', 'Performance Optimization', 'CI/CD & Monitoring'],
                    'resources': [
                        {
                            'resource_id': 'res_prod_01',
                            'title': 'Production Deployment & Observability Best Practices',
                            'resource_type': 'documentation',
                            'duration_minutes': 75,
                            'skills': ['Deployment', 'Monitoring'],
                            'is_mandatory': True,
                        }
                    ],
                    'projects': [
                        {
                            'project_id': 'proj_capstone_01',
                            'title': f'{goal_title} Production Capstone',
                            'description': 'Deploy full production system with live endpoints, monitoring, and documentation.',
                            'difficulty': 'advanced',
                            'estimated_hours': 12,
                            'deliverables': ['Live Deployment', 'Documentation', 'CI/CD Pipeline'],
                        }
                    ],
                    'assessment': 'Final Comprehensive Certification Exam',
                    'assessment_id': 'asm_cap_03',
                    'milestone': 'Capstone portfolio project complete and production ready',
                    'estimated_duration_weeks': 3,
                    'estimated_time': '3 weeks',
                }
            ],
        }
