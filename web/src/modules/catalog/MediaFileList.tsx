import type { MediaFile } from "../../shared/api/types";
import { formatFileSize } from "../../shared/format/fileSize";

interface MediaFileListProps {
  items: MediaFile[];
  selectedId: string;
  busyId?: string;
  onSelect: (media: MediaFile) => void;
  onPreview: (media: MediaFile) => void;
  onDownload: (media: MediaFile) => void;
  onOpenDrive: (media: MediaFile) => void;
}

const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});

function mediaFormat(mediaType: string) {
  return mediaType.split("/").at(-1)?.toUpperCase() || "ARQUIVO";
}

export function MediaFileList({
  items,
  selectedId,
  busyId,
  onSelect,
  onPreview,
  onDownload,
  onOpenDrive,
}: MediaFileListProps) {
  return (
    <div className="media-table" role="table" aria-label="Arquivos do catálogo">
      <div className="media-table-head" role="row">
        <span role="columnheader">Arquivo</span>
        <span role="columnheader">Data</span>
        <span role="columnheader">Formato</span>
        <span role="columnheader">Tamanho</span>
        <span role="columnheader">Status</span>
        <span role="columnheader">Ações</span>
      </div>
      <div className="media-list" role="rowgroup">
        {items.map((item) => {
          const isVideo = item.media_type.startsWith("video/");
          const isBusy = busyId === item.id;
          return (
            <article className={`media-row ${selectedId === item.id ? "selected" : ""}`} key={item.id} role="row">
              <span role="cell">
                <button className="media-file-cell" onClick={() => onSelect(item)} type="button">
                  <span className="file-icon">{isVideo ? "▶" : "▣"}</span>
                  <span className="file-main">
                    <strong>{item.display_name}</strong>
                    <small>{item.tags.map((tag) => tag.name).join(" · ") || item.original_name}</small>
                  </span>
                </button>
              </span>
              <span className="media-date" role="cell">
                {item.recorded_at ? dateFormatter.format(new Date(item.recorded_at)) : "Sem data"}
              </span>
              <span className="media-format" role="cell">{mediaFormat(item.media_type)}</span>
              <span role="cell">{formatFileSize(item.size_bytes)}</span>
              <span role="cell"><span className="status-pill">{item.status}</span></span>
              <span className="media-actions" role="cell">
                <button className="table-action" onClick={() => onSelect(item)} type="button">Detalhes</button>
                {isVideo ? <button className="table-action" onClick={() => onPreview(item)} type="button">Assistir</button> : null}
                <button className="table-action" disabled={isBusy} onClick={() => onDownload(item)} type="button">Baixar</button>
                <button className="table-action" disabled={isBusy} onClick={() => onOpenDrive(item)} type="button">Drive</button>
              </span>
            </article>
          );
        })}
      </div>
    </div>
  );
}
