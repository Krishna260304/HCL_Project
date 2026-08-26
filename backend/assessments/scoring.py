from typing import Any, Dict, List

class DeterministicScoringEngine:
    @classmethod
    def evaluate_answer(cls, question_type: str, correct_answer: Any, submitted_answer: Any) -> bool:
        if submitted_answer is None:
            return False

        if question_type in ('single_select', 'dropdown'):
            return str(correct_answer).strip().lower() == str(submitted_answer).strip().lower()

        if question_type == 'boolean':
            return bool(correct_answer) == bool(submitted_answer)

        if question_type == 'multi_select':
            if not isinstance(correct_answer, list) or not isinstance(submitted_answer, list):
                return False
            correct_set = {str(item).strip().lower() for item in correct_answer}
            submitted_set = {str(item).strip().lower() for item in submitted_answer}
            return correct_set == submitted_set

        if question_type == 'number' or question_type == 'slider':
            try:
                return float(correct_answer) == float(submitted_answer)
            except (ValueError, TypeError):
                return False

        if question_type == 'text':
            return str(correct_answer).strip().lower() == str(submitted_answer).strip().lower()

        return str(correct_answer).strip() == str(submitted_answer).strip()

    @classmethod
    def calculate_assessment_result(
        cls,
        questions: List[Dict[str, Any]],
        submitted_answers: Dict[str, Any],
        passing_score: float = 70.0
    ) -> Dict[str, Any]:
        total_questions = len(questions)
        if total_questions == 0:
            return {
                'score': 0,
                'total_questions': 0,
                'percentage': 0.0,
                'passed': False,
                'skill_scores': {},
                'topic_scores': {},
                'strengths': [],
                'weaknesses': [],
                'detailed_breakdown': [],
            }

        correct_count = 0
        skill_totals: Dict[str, int] = {}
        skill_correct: Dict[str, int] = {}
        topic_totals: Dict[str, int] = {}
        topic_correct: Dict[str, int] = {}
        detailed_breakdown: List[Dict[str, Any]] = []

        for q in questions:
            qid = str(q.get('_id', q.get('id', '')))
            q_type = q.get('type', 'single_select')
            correct_val = q.get('correct_answer')
            sub_val = submitted_answers.get(qid)
            skill_id = str(q.get('skill_id', 'general'))
            topic = str(q.get('topic', 'general'))

            skill_totals[skill_id] = skill_totals.get(skill_id, 0) + 1
            topic_totals[topic] = topic_totals.get(topic, 0) + 1

            is_correct = cls.evaluate_answer(q_type, correct_val, sub_val)
            if is_correct:
                correct_count += 1
                skill_correct[skill_id] = skill_correct.get(skill_id, 0) + 1
                topic_correct[topic] = topic_correct.get(topic, 0) + 1

            detailed_breakdown.append({
                'question_id': qid,
                'skill_id': skill_id,
                'topic': topic,
                'is_correct': is_correct,
                'submitted_answer': sub_val,
                'explanation': q.get('explanation', ''),
            })

        percentage = round((correct_count / total_questions) * 100.0, 2)
        passed = percentage >= passing_score

        skill_scores: Dict[str, Dict[str, Any]] = {}
        strengths: List[str] = []
        weaknesses: List[str] = []

        for sid, count in skill_totals.items():
            s_corr = skill_correct.get(sid, 0)
            s_pct = round((s_corr / count) * 100.0, 2)
            skill_scores[sid] = {
                'total': count,
                'correct': s_corr,
                'percentage': s_pct,
            }
            if s_pct >= 75.0:
                strengths.append(sid)
            elif s_pct < 60.0:
                weaknesses.append(sid)

        topic_scores: Dict[str, Dict[str, Any]] = {}
        for top, count in topic_totals.items():
            t_corr = topic_correct.get(top, 0)
            t_pct = round((t_corr / count) * 100.0, 2)
            topic_scores[top] = {
                'total': count,
                'correct': t_corr,
                'percentage': t_pct,
            }

        return {
            'score': correct_count,
            'total_questions': total_questions,
            'percentage': percentage,
            'passed': passed,
            'skill_scores': skill_scores,
            'topic_scores': topic_scores,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'detailed_breakdown': detailed_breakdown,
        }
