import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";

import type { BackendClient } from "../../shared/api/backendClient";
import type { Project, UploadBatchDetail } from "../../shared/api/types";
import { formatFileSize } from "../../shared/format/fileSize";

interface Props {
  api: BackendClient;
  companyId: string;
  projectId: string;
  projects: Project[];
}

const terminalStatuses = new Set(["SUCCEEDED", "FAILED", "CANCELLED"]);
const categoryLabels = { ORIGINAIS: "Originais", PREVIEWS: "Previews", ENTREGAS: "Entregas" } as const;

function today() {
  const value = new Date();
  return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`;
}

function friendlyError(error: Error | null) {
  if (!error) return "";
  const text = error.message.toLowerCase();
  if (text.includes("conta google")) return "Conecte a conta Google antes de criar o lote.";
  if (text.includes("pastas") || text.includes("árvore")) return "Não foi possível preparar a pasta de destino. Tente novamente.";
  if (text.includes("outro lote") || text.includes("conflito")) return "Um dos arquivos já está em outro envio.";
  if (text.includes("network") || text.includes("fetch")) return "Sem conexão com o servidor. Verifique a internet e tente novamente.";
  if (text.includes("autentica") || text.includes("401")) return "Sua sessão expirou. Entre novamente para continuar.";
  if (text.includes("quota") || text.includes("cota")) return "O Google Drive está sem espaço disponível.";
  if (text.includes("disk") || text.includes("disco")) return "O disco do arquivo não está disponível. Reconecte-o e retome.";
  if (text.includes("integrity") || text.includes("integridade")) return "O arquivo mudou desde a análise e não pode ser enviado.";
  return error.message || "Não foi possível concluir a operação. Tente novamente.";
}

export function UploadBatchPanel({ api, companyId, projectId, projects }: Props) {
  const queryClient = useQueryClient();
  const storageKey = `legado:upload-batch:${companyId}`;
  const [formProjectId, setFormProjectId] = useState(projectId);
  const [folderDate, setFolderDate] = useState(today);
  const [category, setCategory] = useState<keyof typeof categoryLabels>("ORIGINAIS");
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [activeBatchId, setActiveBatchId] = useState(() => sessionStorage.getItem(storageKey) ?? "");
  const idempotencyKey = useRef(crypto.randomUUID());

  useEffect(() => setFormProjectId(projectId), [projectId]);
  useEffect(() => {
    if (activeBatchId) sessionStorage.setItem(storageKey, activeBatchId);
  }, [activeBatchId, storageKey]);

  const batches = useQuery({
    queryKey: ["upload-batches", companyId],
    queryFn: () => api.uploadBatches(companyId),
    enabled: Boolean(companyId),
    refetchInterval: 5000,
  });
  const projectFiles = useQuery({
    queryKey: ["media", companyId, formProjectId, ""],
    queryFn: () => api.mediaFiles(companyId, formProjectId),
    enabled: Boolean(companyId && formProjectId),
  });
  useEffect(() => {
    if (!activeBatchId && batches.data?.items[0]) setActiveBatchId(batches.data.items[0].id);
  }, [activeBatchId, batches.data]);

  const detail = useQuery({
    queryKey: ["upload-batch", companyId, activeBatchId],
    queryFn: () => api.uploadBatch(companyId, activeBatchId),
    enabled: Boolean(companyId && activeBatchId),
    refetchInterval: (query) => terminalStatuses.has((query.state.data as UploadBatchDetail | undefined)?.status ?? "") ? false : 2000,
  });

  const availableFiles = useMemo(
    () => (projectFiles.data?.items ?? []).filter((file) => file.source_machine_id),
    [projectFiles.data],
  );

  const createBatch = useMutation({
    mutationFn: async () => {
      const chosen = availableFiles.filter((file) => selectedFiles.includes(file.id));
      if (!chosen.length) throw new Error("Selecione ao menos um arquivo para enviar.");
      const machines = new Set(chosen.map((file) => file.source_machine_id));
      if (machines.size !== 1) throw new Error("Selecione arquivos da mesma máquina para este lote.");
      await api.ensureDriveFolders(companyId, formProjectId, folderDate);
      return api.createUploadBatch(companyId, {
        project_id: formProjectId,
        machine_id: chosen[0].source_machine_id!,
        folder_date: folderDate,
        idempotency_key: idempotencyKey.current,
        items: chosen.map((file) => ({
          file_version_id: file.file_version_id,
          destination_category: category,
          final_name: file.original_name,
        })),
      });
    },
    onSuccess: async (created) => {
      setActiveBatchId(created.id);
      setSelectedFiles([]);
      idempotencyKey.current = crypto.randomUUID();
      queryClient.setQueryData(["upload-batch", companyId, created.id], created);
      await queryClient.invalidateQueries({ queryKey: ["upload-batches", companyId] });
    },
  });
  const current = detail.data;
  const controlBatch = useMutation({
    mutationFn: (action: "PAUSE" | "RESUME" | "CANCEL") => {
      if (!current) throw new Error("Selecione um lote.");
      return api.controlUploadBatch(companyId, current.id, action, current.version, crypto.randomUUID());
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(["upload-batch", companyId, updated.id], updated);
      void queryClient.invalidateQueries({ queryKey: ["upload-batches", companyId] });
    },
  });

  const error = createBatch.error || controlBatch.error || batches.error || detail.error || projectFiles.error;

  return (
    <section className="upload-panel" id="uploads" aria-labelledby="upload-title">
      <div className="upload-heading">
        <div><span className="eyebrow">Envios ao Google Drive</span><h2 id="upload-title">Lotes de arquivos</h2></div>
        {current && <span className="status-pill">{current.status}</span>}
      </div>
      {error && <p className="inline-error" role="alert">{friendlyError(error)}</p>}

      <form className="batch-form" onSubmit={(event) => { event.preventDefault(); createBatch.mutate(); }}>
        <label>Projeto<select value={formProjectId} onChange={(event) => { setFormProjectId(event.target.value); setSelectedFiles([]); }}>{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label>
        <label>Data<input type="date" value={folderDate} onChange={(event) => setFolderDate(event.target.value)} /></label>
        <label>Categoria<select value={category} onChange={(event) => setCategory(event.target.value as keyof typeof categoryLabels)}>{Object.entries(categoryLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        <button className="primary-button" type="submit" disabled={createBatch.isPending || !selectedFiles.length}>{createBatch.isPending ? "Criando lote…" : `Criar lote (${selectedFiles.length})`}</button>
      </form>

      <div className="batch-files" aria-label="Arquivos disponíveis">
        {availableFiles.length ? availableFiles.map((file) => <label key={file.id} className="batch-file-option"><input type="checkbox" checked={selectedFiles.includes(file.id)} onChange={(event) => setSelectedFiles((currentFiles) => event.target.checked ? [...currentFiles, file.id] : currentFiles.filter((id) => id !== file.id))} /><span><strong>{file.display_name}</strong><small>{formatFileSize(file.size_bytes)}</small></span></label>) : <p className="muted-message">Nenhum arquivo disponível neste projeto.</p>}
      </div>

      {(batches.data?.items.length ?? 0) > 0 && <div className="batch-history"><label>Lote exibido<select value={activeBatchId} onChange={(event) => setActiveBatchId(event.target.value)}>{batches.data?.items.map((batch) => <option key={batch.id} value={batch.id}>{new Date(batch.created_at).toLocaleString("pt-BR")} · {batch.total_items} arquivo(s)</option>)}</select></label></div>}

      {current && <div className="batch-progress">
        <div className="batch-controls">
          {current.status === "PAUSED" || current.status === "PAUSE_REQUESTED" || current.status === "INTERRUPTED" ?
            <button className="primary-button" type="button" disabled={controlBatch.isPending} onClick={() => controlBatch.mutate("RESUME")}>Retomar</button> :
            <button className="ghost-button dark" type="button" disabled={controlBatch.isPending || terminalStatuses.has(current.status)} onClick={() => controlBatch.mutate("PAUSE")}>Pausar</button>}
          <button className="ghost-button dark danger-button" type="button" disabled={controlBatch.isPending || terminalStatuses.has(current.status)} onClick={() => controlBatch.mutate("CANCEL")}>Cancelar</button>
        </div>
        <div className="progress-label"><strong>Progresso geral</strong><span>{current.progress_percent}% · {formatFileSize(current.confirmed_bytes)} de {formatFileSize(current.total_bytes)}</span></div>
        <progress value={current.progress_percent} max="100" />
        <div className="batch-item-list">{current.items.map((item) => <article key={item.id}><div className="progress-label"><strong>{item.final_name}</strong><span>{item.progress_percent}% · {formatFileSize(item.confirmed_bytes)} de {formatFileSize(item.size_bytes)}</span></div><progress value={item.progress_percent} max="100" /><small>{categoryLabels[item.destination_category]} · {item.status}</small></article>)}</div>
      </div>}
    </section>
  );
}
