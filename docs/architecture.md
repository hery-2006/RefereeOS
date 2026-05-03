# RefereeOS Architecture

```mermaid
flowchart TD
    A[Fixture or PDF Upload] --> B[FastAPI API]
    B --> C[Parser]
    C --> D[Evidence Board JSON]
    D --> E[AG2 Agents]
    E --> F[Daytona Repro Sandbox]
    F --> G[Gemini Pro 3.1]
    G --> D
    D --> H[Area Chair Packet]
    H --> I[React Dashboard]
```

The MVP uses deterministic task functions around named AG2 agents so the hackathon demo remains repeatable. When AG2 is installed, the backend creates AG2 `ConversableAgent` instances for the agent roster.

Daytona is the preferred reproducibility runtime. If the SDK or API key is missing locally, the backend marks the receipt as a local fallback instead of pretending a sandbox run occurred.
