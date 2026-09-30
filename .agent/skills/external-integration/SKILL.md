# External Integration Skill

Use when a task adds or modifies an API, SDK, cloud service, hardware interface, authentication flow, webhook, or other external boundary.

## Procedure

1. Identify the exact service and interface.
2. Inspect the repository for existing usage.
3. Verify current authoritative documentation.
4. Confirm version, auth, environment restrictions, request/response/event shape, and failure behavior.
5. Write down only the facts that matter to the implementation.
6. Implement the smallest integration path.
7. Exercise the real boundary where feasible.
8. Verify the user-visible or downstream behavior, not just initialization.

## Red flags

- plausible but undocumented method names
- adding a backend proxy without evidence it is required
- adding a package before checking existing dependencies
- declaring success after a build-only check
- changing architecture to compensate for an unverified API assumption
