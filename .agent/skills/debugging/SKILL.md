# Debugging Skill

Use when behavior is failing, inconsistent, or unexplained.

## Procedure

1. Reproduce the failure.
2. Capture the exact error/output.
3. Identify the smallest failing boundary.
4. Form a root-cause hypothesis.
5. Test the hypothesis with the smallest useful observation or experiment.
6. Fix the root cause.
7. Re-run the original reproduction.
8. Run the relevant regression checks.

## Red flags

- changing several unrelated variables at once
- retrying without learning from the previous failure
- suppressing an error instead of understanding it
- rewriting a subsystem before identifying the failing boundary
- relying on "should work" without a fresh reproduction
