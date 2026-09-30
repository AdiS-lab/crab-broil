# Reusable Prompts

## Start a new implementation task

Read `AGENTS.md`, then inspect `task.md` and the relevant existing code. Do not modify anything until you understand the current implementation and identify material unknowns. For any external API/SDK behavior that matters, verify it against current authoritative documentation. Then implement the smallest solution that satisfies the task and verify the actual acceptance criteria. Do not claim completion without evidence.

## Start a complex feature/integration

Treat `task.md` as the specification. First establish the current architecture, identify relevant files and external interfaces, and resolve unknowns that could change the design. Produce a concise implementation plan only if the work spans multiple files, systems, or architectural decisions. Then implement the smallest coherent solution, verify the real user flow, update `.agent/state.md` with material facts, and report only what is verified.

## Debug a failure

First reproduce the failure. Then isolate the smallest failing boundary and determine the root cause before changing code. Make the smallest fix, add or run a regression check, and reproduce the original flow again. Do not paper over the failure with unrelated refactors or retries that hide the cause.

## Continue after compaction or a long pause

Read `AGENTS.md`, `.agent/state.md`, and the current `task.md`. Trust verified facts recorded in state; re-check assumptions that are no longer supported by the repository. Continue from the `Next concrete action` rather than restarting broad exploration.

## External service integration

Do not code from memory. Identify the exact service/API/SDK and version, verify current official documentation, confirm browser/server restrictions and authentication, inspect the existing project integration pattern, implement the smallest path, and verify the real end-to-end interaction.
