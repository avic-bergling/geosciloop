"""Validate GeoSciLoop project guidance and repo-local skills.

This script intentionally uses only the Python standard library so it can run
in offline CI and fresh development environments.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SKILLS = [
    "geospatial-research-planner",
    "geospatial-python-validator",
    "reproducibility-ledger",
    "benchmark-evaluator",
    "scientific-report-writer",
    "harness-architect",
]

REQUIRED_SKILL_SECTIONS = [
    "## When to use this skill",
    "## What to inspect first",
    "## Required workflow",
    "## Required outputs",
    "## Common failure modes",
    "## Done criteria",
]

REQUIRED_SKILL_DESCRIPTION_TERMS = {
    "geospatial-research-planner": [
        "remote-sensing",
        "GIS",
        "research question",
        "hypotheses",
    ],
    "geospatial-python-validator": [
        "Python",
        "geospatial",
        "remote-sensing",
        "validators",
        "model diagnostics",
    ],
    "reproducibility-ledger": [
        "provenance",
        "manifests",
        "research ledgers",
        "scientific evidence chains",
    ],
    "benchmark-evaluator": [
        "evaluation logic",
        "tests",
        "scoring",
        "benchmark",
    ],
    "scientific-report-writer": [
        "reports",
        "scientific summaries",
        "limitations",
        "artifacts",
    ],
    "harness-architect": [
        "LangGraph",
        "CrewAI",
        "AutoGen",
        "Snakemake",
        "Prefect",
        "Codex subagents",
        "simple runner",
    ],
}

REQUIRED_SKILL_BODY_TERMS = {
    "harness-architect": [
        "explicitly requested",
        "independently reviewed",
        "offline deterministic v0.1",
    ],
}

REQUIRED_GUIDANCE_FILES = [
    "AGENTS.md",
    "docs/harness_strategy.md",
    "docs/skills_usage.md",
    "docs/codex_workflow.md",
    "docs/decisions.md",
    "docs/roadmap.md",
]

REQUIRED_DOC_TERMS = {
    "docs/harness_strategy.md": [
        "deterministic Python runner",
        "LangGraph",
        "Snakemake",
        "Prefect",
        "Codex subagents",
        "OpenAI Agents SDK",
        "v0.1",
        "v0.5",
    ],
    "docs/skills_usage.md": [
        "geospatial-research-planner",
        "geospatial-python-validator",
        "reproducibility-ledger",
        "benchmark-evaluator",
        "scientific-report-writer",
        "harness-architect",
        "$geospatial-research-planner",
    ],
    "docs/codex_workflow.md": [
        "Goal Mode",
        "Superpowers",
        "AGENTS.md",
        "repo-local skills",
        "pytest",
        "subagents",
    ],
    "docs/decisions.md": [
        "deterministic Python runner",
        "repo-local skills",
        "validators and ledger",
        "all tests must be offline",
        "real GEE/STAC support is deferred",
    ],
    "docs/roadmap.md": ["v0.1", "v0.2", "v0.3", "v0.4", "v0.5"],
}

REQUIRED_AGENTS_TERMS = [
    "offline",
    "deterministic",
    "Urban Heat Island",
    "CRS",
    "NoData",
    "LST is not the same as air temperature",
]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def check_frontmatter(path: Path, expected_name: str, failures: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path} is missing YAML frontmatter", failures)
        return

    match = re.match(r"---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail(f"{path} frontmatter is not closed", failures)
        return

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')

    if fields.get("name") != expected_name:
        fail(f"{path} has name={fields.get('name')!r}, expected {expected_name!r}", failures)
    if not fields.get("description"):
        fail(f"{path} is missing description", failures)
    elif "Use when" not in fields["description"]:
        fail(f"{path} description should state when to use the skill", failures)
    else:
        for term in REQUIRED_SKILL_DESCRIPTION_TERMS.get(expected_name, []):
            if term not in fields["description"]:
                fail(f"{path} description missing selection term: {term}", failures)


def check_skill(path: Path, expected_name: str, failures: list[str]) -> None:
    if not path.exists():
        fail(f"missing skill file {path}", failures)
        return

    text = path.read_text(encoding="utf-8")
    check_frontmatter(path, expected_name, failures)
    for section in REQUIRED_SKILL_SECTIONS:
        if section not in text:
            fail(f"{path} missing section {section}", failures)
    for term in REQUIRED_SKILL_BODY_TERMS.get(expected_name, []):
        if term not in text:
            fail(f"{path} missing required body term: {term}", failures)


def check_guidance_file(relative_path: str, failures: list[str]) -> None:
    path = ROOT / relative_path
    if not path.exists():
        fail(f"missing guidance file {relative_path}", failures)
        return
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        fail(f"{relative_path} is empty", failures)
        return
    for term in REQUIRED_DOC_TERMS.get(relative_path, []):
        if term not in text:
            fail(f"{relative_path} missing required term: {term}", failures)


def main() -> int:
    failures: list[str] = []

    for relative_path in REQUIRED_GUIDANCE_FILES:
        check_guidance_file(relative_path, failures)

    agents = ROOT / "AGENTS.md"
    if agents.exists():
        agents_text = agents.read_text(encoding="utf-8")
        for term in REQUIRED_AGENTS_TERMS:
            if term not in agents_text:
                fail(f"AGENTS.md missing required term: {term}", failures)

    for skill_name in EXPECTED_SKILLS:
        skill_path = ROOT / ".agents" / "skills" / skill_name / "SKILL.md"
        check_skill(skill_path, skill_name, failures)

    if failures:
        print(f"\n{len(failures)} validation issue(s) found.")
        return 1

    print("PASS: GeoSciLoop guidance files and repo-local skills are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
