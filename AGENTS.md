# Agent Operating Contract

This file is the small, always-on contract for this repository. Keep it stable, factual, and concise.

## Priority

- Follow the user's current request.
- Follow this repository contract and any more-specific applicable instructions.
- Never invent facts, APIs, files, commands, credentials, or requirements.

## Before changing code

- Inspect the relevant existing implementation first.
- Identify the smallest set of files that can solve the request.
- Reuse existing patterns and dependencies when appropriate.
- Verify uncertain external behavior against current authoritative documentation.
- Distinguish verified facts from assumptions.

Do not scan the whole repository or read every document unless the task requires it.

## Scope

- Make the smallest coherent change that satisfies the request.
- Do not refactor unrelated code, add speculative abstractions, or introduce unnecessary dependencies.
- Do not redesign architecture merely because an initial implementation path failed.

## Execution

Match the workflow to the task:

- Small change: inspect → change → focused verification.
- Feature/integration: inspect → resolve material unknowns → implement → verify.
- Debugging: reproduce → isolate → fix root cause → regression-check.
- Review/research: inspect evidence → analyze → report facts, uncertainty, and tradeoffs.

Do not perform a full plan ceremony for trivial work. For substantial work, make the implementation decisions explicit before committing to them.

## External boundaries

For APIs, SDKs, libraries, cloud services, hardware, or platform behavior:

- Prefer current official documentation.
- Confirm the exact interface, version, authentication, environment restrictions, and required configuration.
- Never manufacture plausible method names or configuration keys.
- Record durable verified facts in `.agent/knowledge.md` when useful.

## Verification

Code generation is not completion. Verify the behavior required by the task.

Before claiming completion:

- check acceptance criteria
- run relevant verification
- inspect the final diff
- state any remaining limitation

For user-facing or external integrations, test the real flow when feasible rather than stopping at compilation or initialization.

## Continuity

For multi-turn work, use `.agent/state.md` to preserve only material state: objective, completed work, active assumptions, blockers, identifiers, last verification, and next action.

Use:

- `project.md` — stable project facts
- `task.md` — current task and acceptance criteria
- `.agent/state.md` — current working state
- `.agent/decisions.md` — durable decisions
- `.agent/knowledge.md` — verified reusable facts
- `.agent/skills/` — specialized workflows

Load these progressively; do not duplicate context across files.

## Drift control

If a failure invalidates an assumption, reassess the approach before adding complexity. Do not spiral into unrelated edits or a second architecture.

If the user starts a new request, do not continue an older task unless the new request clearly depends on it.

## Time and dates

Do not store the current date/time in static instructions. When time matters, use runtime/session context or the model's current date awareness. Supply an explicit timezone only when the task depends on a non-UTC reference.

## Security

Never commit or expose secrets. Treat production and destructive operations as higher-risk than local development.
