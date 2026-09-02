import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { MediaFile } from "../../shared/api/types";
import { MediaFileList } from "./MediaFileList";

const media = {
  id: "media-1",
  project_id: "project-1",
  display_name: "Campanha principal.mp4",
  original_name: "camera-a-001.mp4",
  media_type: "video/mp4",
  description: "",
  observations: "",
  size_bytes: 1048576,
  file_version_id: "version-1",
  source_machine_id: null,
  checksum: { algorithm: "SHA256", digest: "abc123" },
  recorded_at: "2026-09-01T12:00:00Z",
  status: "ORGANIZADO",
  version: 1,
  tags: [{ id: "tag-1", name: "Campanha", is_system: false }],
} as MediaFile;

describe("MediaFileList", () => {
  it("exibe os arquivos em colunas e oferece as ações principais", () => {
    const onSelect = vi.fn();
    const onPreview = vi.fn();
    const onDownload = vi.fn();
    const onOpenDrive = vi.fn();

    render(
      <MediaFileList
        items={[media]}
        selectedId=""
        onSelect={onSelect}
        onPreview={onPreview}
        onDownload={onDownload}
        onOpenDrive={onOpenDrive}
      />,
    );

    expect(screen.getByRole("table", { name: "Arquivos do catálogo" })).toBeInTheDocument();
    expect(screen.getByText("Campanha principal.mp4")).toBeInTheDocument();
    expect(screen.getByText("MP4")).toBeInTheDocument();
    expect(screen.getByText("1 MB")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Assistir" }));
    fireEvent.click(screen.getByRole("button", { name: "Baixar" }));
    fireEvent.click(screen.getByRole("button", { name: "Drive" }));
    expect(onPreview).toHaveBeenCalledWith(media);
    expect(onDownload).toHaveBeenCalledWith(media);
    expect(onOpenDrive).toHaveBeenCalledWith(media);
  });
});
