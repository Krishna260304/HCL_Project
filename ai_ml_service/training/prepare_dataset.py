"""Build a domain-specific instruction dataset for LearnPath.

The generated examples are synthetic and intentionally small. External data is
opt-in: pass reviewed Hugging Face dataset IDs with --hf-dataset and preserve
the source/license metadata in the resulting JSONL. This avoids silently
training on data whose license or personal-data status is unknown.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

SKILLS = {
    "python": ("Python", "Write a small function, test it, and explain the trade-offs."),
    "sql": ("SQL", "Query a relational database, validate the result, and explain indexing."),
    "machine_learning": ("machine learning", "Define a measurable target, split data correctly, and evaluate a baseline."),
    "frontend": ("frontend engineering", "Build an accessible, responsive interface with loading and error states."),
    "cloud": ("cloud engineering", "Deploy a small service with health checks, logs, secrets, and rollback."),
}


def synthetic_records(seed: int, per_skill: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    records: list[dict[str, Any]] = []
    patterns = [
        "I have {hours} hours per week and want to become a {role}. What should I learn next?",
        "How do I prove that I can use {skill} in a professional project?",
        "I am stuck on {skill}. Give me a hint, not the full solution.",
        "Create a diagnostic question for {skill} and explain why the answer is correct.",
    ]
    roles = ["software engineer", "data scientist", "ML engineer", "cloud engineer", "frontend developer"]
    for key, (skill, proof) in SKILLS.items():
        for _ in range(per_skill):
            request = rng.choice(patterns).format(skill=skill, hours=rng.choice([3, 5, 8, 12]), role=rng.choice(roles))
            answer = (
                f"Start with one observable milestone for {skill}. {proof} "
                "Use a small project, record the result, and reassess before adding another topic. "
                "If your goal or experience differs, adjust the difficulty rather than skipping the prerequisite."
            )
            records.append({
                "messages": [
                    {"role": "system", "content": "You are LearnPath AI, a precise and encouraging learning coach. Ground advice in the learner context and never invent completed evidence."},
                    {"role": "user", "content": request},
                    {"role": "assistant", "content": answer},
                ],
                "metadata": {"source": "synthetic", "skill": key, "license": "original"},
            })
    return records


def load_hf_dataset(dataset_id: str, split: str) -> list[dict[str, Any]]:
    from datasets import load_dataset
    dataset = load_dataset(dataset_id, split=split)
    rows = []
    for row in dataset:
        # Accept common instruction formats, but do not guess at arbitrary
        # columns: malformed rows are excluded instead of becoming bad data.
        instruction = row.get("instruction") or row.get("question") or row.get("prompt")
        response = row.get("output") or row.get("answer") or row.get("response")
        if isinstance(instruction, str) and isinstance(response, str) and instruction.strip() and response.strip():
            rows.append({
                "messages": [
                    {"role": "system", "content": "You are LearnPath AI, a precise and encouraging learning coach."},
                    {"role": "user", "content": instruction.strip()},
                    {"role": "assistant", "content": response.strip()},
                ],
                "metadata": {"source": dataset_id, "license": "REVIEWED_BY_OPERATOR"},
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/learnpath_train.jsonl"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--per-skill", type=int, default=40)
    parser.add_argument("--hf-dataset", action="append", default=[], help="Reviewed HF dataset ID; repeatable")
    parser.add_argument("--hf-split", default="train")
    args = parser.parse_args()

    rows = synthetic_records(args.seed, args.per_skill)
    for dataset_id in args.hf_dataset:
        rows.extend(load_hf_dataset(dataset_id, args.hf_split))
    random.Random(args.seed).shuffle(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} records to {args.output}")


if __name__ == "__main__":
    main()
