# ADR-001: local reference stack

Status: accepted for the reference lab.

Use FastAPI/Pydantic for the executable control plane, PostgreSQL as the production-shaped relational boundary, Redis Streams for queue/outbox fixtures, MinIO for S3-compatible artifact storage, OpenTelemetry Collector for telemetry, and Next.js for the portal. The default unit test path uses deterministic in-memory ports so correctness does not depend on Docker. Compose is mandatory as an integration gate.

Redis Streams was selected over RabbitMQ because the reference lab needs a compact local topology and stream identity/replay semantics. This is not a universal production recommendation; sustained throughput and operational ownership must be re-evaluated before productization.

