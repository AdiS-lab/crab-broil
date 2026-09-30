# Context Policy

## Goal

Maximize useful context, not context volume.

## Load order

Prefer:

1. current user request
2. `task.md`
3. relevant source/configuration
4. `project.md` sections relevant to the task
5. `.agent/state.md` for multi-turn work
6. `.agent/decisions.md` when architecture is involved
7. `.agent/knowledge.md` when a previously verified fact is relevant
8. specialized skills/docs only when the task triggers them

## Progressive disclosure

Do not read every document at the start of every task.

Search first, then expand only the files or sections needed to answer the current question.

## Compaction/long tasks

Preserve these facts when context is compacted:

- current objective
- completed actions
- active assumptions
- important IDs/paths
- tool/test outcomes
- unresolved blockers
- next concrete action

## Separation

- Instructions belong in `AGENTS.md`.
- Stable facts belong in `project.md`.
- Current task requirements belong in `task.md`.
- Current factual state belongs in `.agent/state.md`.
- Durable decisions belong in `.agent/decisions.md`.
- Reusable verified facts belong in `.agent/knowledge.md`.
- Specialized procedures belong in skills.
