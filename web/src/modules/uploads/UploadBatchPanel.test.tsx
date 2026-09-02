import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { BackendClient } from "../../shared/api/backendClient";
import { UploadBatchPanel } from "./UploadBatchPanel";

describe("UploadBatchPanel", () => {
  it("abre em modal e mostra somente os lotes do projeto atual", async () => {
    const currentBatch = {
      id: "batch-current",
      project_id: "project-current",
      status: "SUCCEEDED",
      total_items: 1,
      created_at: "2026-09-01T12:00:00Z",
    };
    const otherBatch = {
      id: "batch-other",
      project_id: "project-other",
      status: "SUCCEEDED",
      total_items: 2,
      created_at: "2026-08-30T12:00:00Z",
    };
    const api = {
      uploadBatches: vi.fn().mockResolvedValue({ items: [otherBatch, currentBatch], next_cursor: null }),
      mediaFiles: vi.fn().mockResolvedValue({ items: [], next_cursor: null }),
      uploadBatch: vi.fn().mockResolvedValue({
        ...currentBatch,
        machine_id: "machine-1",
        drive_account_id: "drive-1",
        folder_date: "2026-09-01",
        total_bytes: 10,
        confirmed_bytes: 10,
        progress_percent: 100,
        version: 1,
        items: [],
      }),
      uploadRealtimeTicket: vi.fn().mockReturnValue(new Promise(() => undefined)),
    } as unknown as BackendClient;

    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <UploadBatchPanel
          api={api}
          companyId="company-1"
          projectId="project-current"
          projects={[
            { id: "project-current", name: "São João" },
            { id: "project-other", name: "Outro projeto" },
          ] as never}
        />
      </QueryClientProvider>,
    );

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Gerenciar envios/i }));

    expect(await screen.findByRole("heading", { name: "Lotes de São João" })).toBeInTheDocument();
    const batchSelect = await screen.findByRole("combobox", { name: "Lote exibido" });
    expect(within(batchSelect).getAllByRole("option")).toHaveLength(1);
    await waitFor(() => expect(api.uploadBatch).toHaveBeenCalledWith("company-1", "batch-current"));
    expect(api.mediaFiles).toHaveBeenCalledWith("company-1", "project-current");

    fireEvent.click(screen.getByRole("button", { name: "Fechar envios" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
