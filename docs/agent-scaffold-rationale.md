# Agent Scaffold Rationale

This template deliberately separates always-on instructions from task context, state, durable decisions, verified knowledge, and specialized workflows.

## Design choices

### Small root contract

`AGENTS.md` is loaded persistently by several coding-agent environments. Keep it focused on stable rules rather than project history or long procedural checklists.

### Progressive context

`project.md`, `task.md`, `.agent/state.md`, and supporting files are loaded according to the task. Do not force an agent to reread a full repository map or every document for a tiny change.

### State separate from instructions

`.agent/state.md` is factual working memory. It can be regenerated or compacted without changing the repository's behavioral contract.

### Decisions separate from knowledge

A decision records what the project chose. Knowledge records what the project has verified. This prevents assumptions from becoming indistinguishable from architecture.

### Skills separate from the main prompt

Reusable workflows belong in specialized skill files and should be loaded when applicable, rather than bloating every request.

### Runtime context is dynamic

Time, branch, commit, OS, runtime versions, tool availability, and session identifiers are environment state. They should be injected by a harness when useful, not hard-coded into permanent Markdown.

## Compatibility model

- Codex: `AGENTS.md`
- Claude Code: `CLAUDE.md` imports `AGENTS.md`
- GitHub Copilot: `.github/copilot-instructions.md` imports `AGENTS.md`
- Cursor: root `AGENTS.md`; add `.cursor/rules/` only when path-scoped or conditional rules are needed
