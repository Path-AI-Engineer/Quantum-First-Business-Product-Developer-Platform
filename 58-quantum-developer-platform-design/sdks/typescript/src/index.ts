export type Operation =
  | "circuit.sample"
  | "observable.estimate"
  | "optimization.solve"
  | "resource.estimate"
  | "workflow.run";

export interface JobRequest {
  operation: Operation;
  provider: "fake" | "local" | "ibm" | "braket" | "azure";
  payload: Record<string, unknown>;
}

export class QuantumPlatformError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly correlationId: string,
  ) {
    super(message);
  }
}

export class QuantumPlatformClient {
  constructor(private readonly baseUrl: string, private readonly apiKey: string) {}

  async capabilities(): Promise<Record<string, unknown>[]> {
    return this.request("/v1/capabilities");
  }

  async submitJob(projectId: string, body: JobRequest, idempotencyKey: string) {
    if (!idempotencyKey) throw new Error("idempotencyKey is required for job creation");
    return this.request(`/v1/jobs?project_id=${encodeURIComponent(projectId)}`, {
      method: "POST",
      headers: { "Idempotency-Key": idempotencyKey },
      body: JSON.stringify(body),
    });
  }

  private async request(path: string, init: RequestInit = {}) {
    const response = await fetch(`${this.baseUrl.replace(/\/$/, "")}${path}`, {
      ...init,
      headers: { Authorization: `Bearer ${this.apiKey}`, "Content-Type": "application/json", ...init.headers },
    });
    const body = await response.json();
    if (!response.ok) throw new QuantumPlatformError(body.code, body.detail, body.correlation_id);
    return body;
  }
}

