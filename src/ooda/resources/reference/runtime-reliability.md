# Runtime reliability

Load when the mission touches live processes, locking, mutable measurement
substrates, restarts, or partial failure. Lean does not mean reckless — this is
high-consequence work and the protections are the point.

Reason explicitly about: restart, duplication, concurrent writers, stale state,
partial failure, dependency loss, and what happens to in-flight data.

For a mutable substrate under a live writer (e.g. SQLite with a flock):

- establish who currently holds the lock before proposing a change
- never infer "not running" from prose; read the runtime
- a reader must not assume a consistent snapshot without saying how it got one
- migrations against a live writer need an explicit quiesce or a proven-safe path

Required for a change here: reliability reasoning, explicit human authority,
tests that exercise the failure mode, meaningful independent validation, and
durable documentation when a contract changes.
