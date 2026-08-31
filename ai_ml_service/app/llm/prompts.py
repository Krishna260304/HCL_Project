"""
Versioned Prompt Management System.
Loads structured Jinja2/string prompt templates from files with fallback defaults.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import jinja2

DEFAULT_PROMPT_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"

PROMPT_TEMPLATES: Dict[str, str] = {
    "goal_analysis_v1": """
You are an expert curriculum architect and career advisor.
Analyze the following learner goal and background:

Goal: {{ goal }}
Experience Level: {{ experience_level }}
Knowledge Areas: {{ knowledge_areas | join(', ') }}
Learning History: {{ learning_history }}
Target Outcome: {{ target_outcome }}
Timeline: {{ timeline }}

Generate a structured analysis containing:
1. Normalized career / learning goal
2. Goal classification type (career_advancement, skill_advancement, project_mastery, general_learning)
3. Target outcome description
4. Realistic timeline
5. Required foundational domains and recommended domains
6. Specific skills required
7. Possible professional roles
""",

    "assessment_generation_v1": """
You are an expert technical psychometrician.
Generate a high-quality diagnostic multiple-choice assessment for:

Goal: {{ goal }}
Experience Level: {{ experience_level }}
Target Skills: {{ skills | join(', ') }}
Knowledge Areas: {{ knowledge_areas | join(', ') }}
Number of Questions: {{ num_questions }}

Requirements for EACH question:
- question: Clear, concise technical question stem testing practical knowledge.
- options: Exactly 4 plausible and distinct choices.
- correct_answer: The exact string verbatim from options that is correct.
- skill: Target skill evaluated.
- topic: Subtopic tested.
- difficulty: "{{ experience_level }}"
- learning_objective: 1 concise sentence stating the evaluated outcome.
- explanation: 1 concise sentence explaining why the correct answer is right.

Ensure all {{ num_questions }} questions are fully completed in valid JSON. Keep question stems and explanations concise for fast evaluation.
""",

    "question_repair_v1": """
The following question failed validation rules:
Error Reason: {{ error_reason }}
Original Question:
{{ invalid_question }}

Target Skill: {{ skill }}
Target Difficulty: {{ difficulty }}

Regenerate a clean, fully valid multiple-choice question that strictly adheres to:
1. Distinct question stem
2. At least 4 distinct options
3. Correct answer matching one option verbatim
4. Skill, topic, difficulty, learning_objective, and explanation.
""",

    "skill_analysis_v1": """
Analyze the learner's demonstrated competencies based on the following evidence:
Self-Reported Skills: {{ self_reported_skills }}
Assessment Results: {{ assessment_results }}
Learning History: {{ learning_history }}
Goal: {{ goal }}

Compute:
1. Verified skill scores (0.0 to 1.0) strictly based on assessment performance.
2. Estimated skill levels.
3. Identified validated strengths and weaknesses.
4. Specific skill gaps against the target goal.
5. Immediate recommended next skills.
""",

    "resource_analysis_v1": """
Extract structured educational metadata from this learning resource:
Title: {{ title }}
Description: {{ description }}
Source: {{ source }}
URL: {{ url }}

Determine:
1. Relevant skills and granular topics
2. Difficulty tier (beginner, intermediate, advanced)
3. Prerequisite competencies
4. Estimated completion duration in minutes
5. Learning format (video, article, course, documentation, project, exercise)
6. Quality score (0.0 to 1.0) and summary
""",

    "recommendation_explanation_v1": """
Generate a concise, motivating, natural language explanation for why this resource is recommended to the learner.
CRITICAL: Use ONLY the provided evidence. Do NOT hallucinate course features not listed.

Resource Title: {{ resource.title }}
Resource Skills: {{ resource.skills | join(', ') }}
Resource Difficulty: {{ resource.difficulty }}
Learner Goal: {{ goal }}
Matched Skill Gap: {{ evidence.matched_skills | join(', ') }}
Skill Gap Score Before: {{ evidence.skill_gap_match }}

Explain why this resource directly advances the learner's path:
""",

    "learning_path_v1": """
You are a principal curriculum architect.
Design a concise 3-phase personalized learning roadmap for:
Goal: {{ goal }}
Verified Skills: {{ verified_skills }}
Skill Gaps: {{ skill_gaps }}
Timeline: {{ timeline }}

Generate exactly 3 sequential phases:
- Phase 1: Foundations & Core Setup (order: 1)
- Phase 2: Architecture & Hands-on Implementation (order: 2)
- Phase 3: Production Deployment & Capstone Portfolio (order: 3)

For each phase include:
- phase_id ("phase_1", "phase_2", "phase_3")
- title, description, and 1-sentence objective
- order (1, 2, 3)
- skills: target skills
- resources: 1-2 recommended resources (resource_id, title, resource_type: "video" or "documentation", duration_minutes)
- projects: 1 hands-on milestone project (project_id, title, description, difficulty, estimated_hours, deliverables)
- milestone: 1-sentence completion criteria
- estimated_duration_weeks: (int, e.g. 2, 3, 3)

Return ONLY valid JSON matching the schema. Keep descriptions concise for fast execution.
""",

    "rag_v1": """
You are LearnPath AI Tutor, a personalized AI learning mentor.
Answer the learner's query accurately using ONLY the provided verified context documents and learner state.

Learner Context:
{{ learner_context }}

Retrieved Knowledge Documents:
{% for doc in documents %}
[Source {{ loop.index }}] {{ doc.title }} (URL: {{ doc.url }})
{{ doc.snippet }}
{% endfor %}

Learner Query: {{ query }}

Instructions:
1. Base your answer strictly on the retrieved sources and learner state.
2. Directly answer the question in a clear, encouraging pedagogical tone.
3. Suggest 2-3 concrete next steps or actions for the learner.
4. Do not invent sources or facts.
""",

    "assistant_v1": """
You are the LearnPath AI Assistant, interacting with a learner within their personalized learning path.
Learner Context:
- Current Goal: {{ context.current_goal }}
- Current Phase: {{ context.current_phase }}
- Current Topic: {{ context.current_topic }}
- Verified Skills: {{ context.verified_skills }}
- Skill Gaps: {{ context.skill_gaps }}
- Progress: {{ context.progress_percentage }}%

Conversation History:
{{ history }}

Learner Message: {{ message }}

Provide helpful, context-aware guidance and recommend next actions based on where they are in their roadmap.
""",

    "adaptive_learning_v1": """
Evaluate the learner's updated progress and latest assessment results to determine roadmap adaptations:
Previous Roadmap: {{ previous_path }}
Latest Assessment Results: {{ latest_assessment }}
Current Skill Scores: {{ skill_scores }}
Goal: {{ goal }}

Determine:
1. Updated skill scores reflecting new performance.
2. Mastered topics vs topics needing remediation.
3. Roadmap adjustments (insert remedial exercises, fast-track mastered modules, or schedule targeted retests).
4. Clear reasoning for each adaptation.
"""
}


class PromptManager:
    """Manages loading and rendering versioned prompt templates."""

    def __init__(self, prompt_dir: Optional[Path] = None):
        self.prompt_dir = prompt_dir or DEFAULT_PROMPT_DIR
        self._jinja_env = jinja2.Environment(
            undefined=jinja2.StrictUndefined,
            autoescape=False,
        )

    def render(self, template_name: str, **kwargs: Any) -> str:
        """Render a versioned prompt template by name with supplied variables."""
        # Check filesystem first
        template_file = self.prompt_dir / f"{template_name}.txt"
        if template_file.exists():
            template_str = template_file.read_text(encoding="utf-8")
        elif template_name in PROMPT_TEMPLATES:
            template_str = PROMPT_TEMPLATES[template_name]
        else:
            raise KeyError(f"Prompt template '{template_name}' not found.")

        template = self._jinja_env.from_string(template_str)
        return template.render(**kwargs).strip()


_global_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    global _global_prompt_manager
    if _global_prompt_manager is None:
        _global_prompt_manager = PromptManager()
    return _global_prompt_manager
