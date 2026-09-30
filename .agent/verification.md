# Verification Standard

## Principle

The result is the verified behavior, not the generated code.

## Match verification to risk

### Low-risk/local

- typecheck/build/lint where relevant
- focused tests

### Multi-file feature

- focused automated tests
- build/typecheck
- runtime smoke test

### External integration

Verify the real interaction where possible:

1. initialization/auth succeeds
2. request/connection is made
3. expected data or event crosses the boundary
4. expected response is received
5. user-visible behavior occurs
6. failure states are handled

### UI work

Prefer browser/runtime inspection over reasoning from source alone.

### Destructive/production work

Verify target, scope, permissions, and rollback/recovery path before executing.

## Evidence rule

Do not write:

> "This should work."

as a completion claim.

Instead report what was actually observed:

> "Ran X; observed Y; acceptance criterion Z passed."

## Final review

Before completion:

- inspect changed files
- check for accidental edits
- re-read acceptance criteria
- run the relevant verification again if the last code change occurred after the previous verification
