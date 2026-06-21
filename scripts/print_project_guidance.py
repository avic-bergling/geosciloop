"""Print the main GeoSciLoop project guidance files."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

GUIDANCE_FILES = [
    "AGENTS.md",
    "docs/harness_strategy.md",
    "docs/skills_usage.md",
    "docs/codex_workflow.md",
    "docs/decisions.md",
    "docs/roadmap.md",
]

SKILLS = [
    "geospatial-research-planner",
    "geospatial-python-validator",
    "reproducibility-ledger",
    "benchmark-evaluator",
    "scientific-report-writer",
    "harness-architect",
]


def main() -> int:
    print("GeoSciLoop guidance files:")
    for relative_path in GUIDANCE_FILES:
        path = ROOT / relative_path
        status = "present" if path.exists() else "missing"
        print(f"- {relative_path}: {status}")

    print("\nRepo-local skills:")
    for skill in SKILLS:
        path = ROOT / ".agents" / "skills" / skill / "SKILL.md"
        status = "present" if path.exists() else "missing"
        print(f"- {skill}: {status}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
