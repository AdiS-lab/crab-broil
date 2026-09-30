# Agent Workflow

This is a reference workflow. Apply the parts relevant to the current request; do not mechanically execute every phase for trivial changes.

## 1. Frame the request

Determine which kind of work this is:

- answer/explain
- investigate/research
- small change
- feature/integration
- debugging
- review/refactor
- deployment/operational change

Read `task.md` when it contains the active task or when the request is clearly part of that task.

## 2. Establish reality

For implementation work, inspect the relevant code and configuration before deciding how to change it.

Identify:

- existing behavior
- relevant files
- dependencies
- external systems
- unknowns that can change the implementation

Do not treat guesses as facts.

## 3. Plan only when useful

For a small/local change, a full written plan is unnecessary.

For multi-file work, integrations, or architectural changes, define:

- files/components involved
- interface/data-flow changes
- concrete implementation steps
- concrete verification

A plan should capture decisions the implementer should not have to rediscover.

## 4. Implement minimally

Prefer existing architecture and local changes.

Stop and reassess if:

- the required API differs from the assumption
- a new dependency becomes necessary
- the change spreads into unrelated subsystems
- a workaround is turning into a second architecture

## 5. Verify against reality

Verify the acceptance criteria, not merely the implementation's internal consistency.

For integrations, use the real integration where feasible.

For UI, inspect the rendered experience when feasible.

For bugs, verify both the fix and the relevant regression path.

## 6. Preserve state

After material progress, update `.agent/state.md` with the facts another agent turn would need to continue correctly.

Do not turn state into a transcript.

## 7. Finish cleanly

Before completion:

- re-check acceptance criteria
- inspect the diff
- run relevant verification
- distinguish verified results from unverified claims
