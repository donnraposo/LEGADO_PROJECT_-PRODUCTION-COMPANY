import { afterEach, describe, expect, it, vi } from "vitest";

import { BackendClient } from "./backendClient";

describe("BackendClient", () => {
  afterEach(() => vi.restoreAllMocks());

  it("envia token e empresa somente nos cabeçalhos", async () => {
    const request = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [], next_cursor: null }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const client = new BackendClient(async () => "memory-token");

    await client.projects("company-id");

    const [path, init] = request.mock.calls[0];
    const headers = new Headers(init?.headers);
    expect(path).toBe("/api/v1/projects");
    expect(headers.get("Authorization")).toBe("Bearer memory-token");
    expect(headers.get("X-Company-ID")).toBe("company-id");
    expect(JSON.stringify(init)).not.toContain("memory-token");
  });

  it("traduz falhas da API em mensagem segura", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "Acesso negado." }), {
        status: 403,
        headers: { "Content-Type": "application/json" },
      }),
    );
    const client = new BackendClient(async () => "memory-token");

    await expect(client.projects("company-id")).rejects.toThrow("Acesso negado.");
  });
});
