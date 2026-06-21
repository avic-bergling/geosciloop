# Codex Workflow

Use this workflow when asking Codex to work on GeoSciLoop.

1. Start with Goal Mode for large, verifiable milestones.
2. Use Superpowers if available for disciplined planning, TDD, debugging, refactoring, and verification. Do not assume exact Superpowers command names unless they are present in the environment.
3. Use `AGENTS.md` for always-on project rules.
4. Use repo-local skills for task-specific workflows.
5. Treat pytest, standard-library validation scripts, and artifact checks as the validation surface.
6. For complex tasks, ask Codex to split work into checkpoints with concrete files, commands, and done criteria.
7. For future parallel work, use subagents only when explicitly requested and when outputs can be independently reviewed.
8. Keep a short progress log in `docs/decisions.md` or a dedicated plan file for multi-hour work.

For v0.1, prefer deterministic local commands and synthetic data. Do not require internet access, API keys, Google Earth Engine authentication, or full agent orchestration to validate core behavior.
