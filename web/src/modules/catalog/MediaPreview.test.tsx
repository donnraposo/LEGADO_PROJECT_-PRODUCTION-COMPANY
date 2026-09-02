import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { BackendClient } from "../../shared/api/backendClient";
import type { MediaFile } from "../../shared/api/types";
import { MediaPreview } from "./MediaPreview";

describe("MediaPreview", () => {
  it("oferece o link do Google Drive quando o navegador não suporta o formato", async () => {
    vi.spyOn(HTMLMediaElement.prototype, "canPlayType").mockReturnValue("");
    const api = {
      mediaPlayback: vi.fn().mockResolvedValue({
        stream_url: "/api/v1/media-playback/ticket",
        download_url: "/api/v1/media-download/ticket",
        drive_url: "https://drive.google.com/file/d/file-1/view",
        expires_in: 600,
      }),
    } as unknown as BackendClient;
    const media = {
      id: "media-1",
      display_name: "Original em ProRes.mov",
      media_type: "video/quicktime",
    } as MediaFile;

    render(
      <QueryClientProvider client={new QueryClient()}>
        <MediaPreview api={api} companyId="company-1" media={media} onClose={vi.fn()} />
      </QueryClientProvider>,
    );

    const link = await screen.findByRole("link", { name: "Abrir no Google Drive" });
    expect(link).toHaveAttribute(
      "href",
      "https://drive.google.com/file/d/file-1/view",
    );
    expect(link).toHaveAttribute("target", "_blank");
    expect(screen.getByRole("link", { name: "Baixar arquivo" })).toHaveAttribute(
      "href",
      "/api/v1/media-download/ticket",
    );
    expect(api.mediaPlayback).toHaveBeenCalledWith("company-1", "media-1");
  });
});
