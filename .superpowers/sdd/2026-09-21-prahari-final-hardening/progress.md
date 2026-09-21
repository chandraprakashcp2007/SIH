# SDD ledger — plan: docs/superpowers/plans/2026-09-21-prahari-final-hardening.md

Ruling: Work in the existing checkout because the repository has no commit and cannot create a worktree — preserves all untracked user content and avoids committing secrets/runtime data — cost if wrong: implementation is not isolated on a separate branch.
Pre-flight: Task 1 validation outputs feed Tasks 3 and 4; Task 2 auth dependencies protect Tasks 3–7 routes; Task 3 operational contracts feed Tasks 4–7; Task 5 UI consumes Tasks 2–4; Task 6 wraps Task 5 APIs/routes. Interfaces are ordered consistently.
