import { useEffect, useState } from "react";

import type { MediaFile, Tag } from "../../shared/api/types";
import { formatFileSize } from "../../shared/format/fileSize";

interface MediaEditorProps {
  media: MediaFile;
  tags: Tag[];
  busy: boolean;
  onClose: () => void;
  onSave: (values: {
    display_name: string;
    description: string;
    observations: string;
  }) => void;
  onTagChange: (tagId: string, selected: boolean) => void;
  onPreview: () => void;
}

export function MediaEditor({
  media,
  tags,
  busy,
  onClose,
  onSave,
  onTagChange,
  onPreview,
}: MediaEditorProps) {
  const [displayName, setDisplayName] = useState(media.display_name);
  const [description, setDescription] = useState(media.description);
  const [observations, setObservations] = useState(media.observations);

  useEffect(() => {
    setDisplayName(media.display_name);
    setDescription(media.description);
    setObservations(media.observations);
  }, [media]);

  const assigned = new Set(media.tags.map((tag) => tag.id));

  return (
    <aside className="editor-panel" aria-label="Detalhes do arquivo">
      <div className="editor-heading">
        <div>
          <span className="eyebrow">Detalhes do arquivo</span>
          <h2>{media.original_name}</h2>
        </div>
        <button className="icon-button" type="button" onClick={onClose} aria-label="Fechar">
          ×
        </button>
      </div>

      <div className="file-facts">
        <span>{formatFileSize(media.size_bytes)}</span>
        <span>{media.media_type || "Tipo não identificado"}</span>
        <span className="status-pill">{media.status}</span>
      </div>

      {media.media_type.startsWith("video/") && (
        <button className="preview-button" onClick={onPreview} type="button">
          ▶ Assistir vídeo
        </button>
      )}

      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSave({ display_name: displayName, description, observations });
        }}
      >
        <label>
          Nome de exibição
          <input
            required
            maxLength={255}
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
          />
        </label>
        <label>
          Descrição
          <textarea
            rows={3}
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
        </label>
        <label>
          Observações
          <textarea
            rows={3}
            value={observations}
            onChange={(event) => setObservations(event.target.value)}
          />
        </label>
        <button className="primary-button" disabled={busy} type="submit">
          {busy ? "Salvando…" : "Salvar alterações"}
        </button>
      </form>

      <div className="tag-section">
        <h3>Classificações</h3>
        <div className="tag-grid">
          {tags.map((tag) => (
            <label className="tag-option" key={tag.id}>
              <input
                type="checkbox"
                checked={assigned.has(tag.id)}
                disabled={busy}
                onChange={(event) => onTagChange(tag.id, event.target.checked)}
              />
              <span>{tag.name}</span>
            </label>
          ))}
        </div>
      </div>
    </aside>
  );
}
