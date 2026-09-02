import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";

import type { BackendClient } from "../../shared/api/backendClient";
import type { MediaFile } from "../../shared/api/types";
import { Icon } from "../../shared/ui/Icon";

interface MediaPreviewProps {
  api: BackendClient;
  companyId: string;
  media: MediaFile;
  onClose: () => void;
}

export function MediaPreview({ api, companyId, media, onClose }: MediaPreviewProps) {
  const closeButton = useRef<HTMLButtonElement>(null);
  const [playbackFailed, setPlaybackFailed] = useState(false);
  const playback = useQuery({
    queryKey: ["media-playback", companyId, media.id],
    queryFn: () => api.mediaPlayback(companyId, media.id),
    staleTime: 0,
  });
  const browserClaimsSupport = useMemo(() => {
    if (!media.media_type.startsWith("video/")) return false;
    return Boolean(document.createElement("video").canPlayType(media.media_type));
  }, [media.media_type]);

  useEffect(() => {
    closeButton.current?.focus();
    const closeOnEscape = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [onClose]);

  const needsFallback = !browserClaimsSupport || playbackFailed;

  return (
    <div className="video-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section aria-labelledby="video-preview-title" aria-modal="true" className="video-modal" role="dialog">
        <header className="video-modal-header">
          <div><span className="eyebrow">Visualização do arquivo</span><h2 id="video-preview-title">{media.display_name}</h2></div>
          <button aria-label="Fechar vídeo" className="icon-button" onClick={onClose} ref={closeButton} type="button"><Icon name="close" /></button>
        </header>

        <div className="video-stage">
          {playback.isLoading ? (
            <div className="video-message">Preparando reprodução segura…</div>
          ) : playback.error ? (
            <div className="video-message error-message"><strong>Vídeo indisponível</strong><span>{playback.error.message}</span></div>
          ) : needsFallback ? (
            <div className="video-message"><strong>Este formato não pode ser reproduzido no navegador.</strong><span>Abra o arquivo no Google Drive para utilizar a visualização disponível na sua conta.</span><a className="primary-button" href={playback.data?.drive_url} rel="noopener noreferrer" target="_blank">Abrir no Google Drive</a></div>
          ) : (
            <video controls onError={() => setPlaybackFailed(true)} preload="metadata" src={playback.data?.stream_url}>Seu navegador não oferece reprodução de vídeo.</video>
          )}
        </div>
        {playback.data ? (
          <footer className="video-modal-actions">
            <a className="primary-button" href={playback.data.download_url}>Baixar arquivo</a>
          </footer>
        ) : null}
      </section>
    </div>
  );
}
