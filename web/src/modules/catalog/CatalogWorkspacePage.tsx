import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useAuth } from "../authentication/AuthProvider";
import { BackendClient } from "../../shared/api/backendClient";
import type { MediaFile } from "../../shared/api/types";
import { formatFileSize } from "../../shared/format/fileSize";
import { Icon } from "../../shared/ui/Icon";
import { MediaEditor } from "./MediaEditor";
import { MediaFileList } from "./MediaFileList";
import { MediaPreview } from "./MediaPreview";
import { DriveConnectionPanel } from "../drive/DriveConnectionPanel";
import { UploadBatchPanel } from "../uploads/UploadBatchPanel";

export function CatalogWorkspacePage() {
  const { companyId: routeCompanyId, projectId: routeProjectId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const auth = useAuth();
  const api = useMemo(() => new BackendClient(auth.accessToken), [auth.accessToken]);
  const [companyId, setCompanyId] = useState(routeCompanyId ?? "");
  const [projectId, setProjectId] = useState(routeProjectId ?? "");
  const [searchDraft, setSearchDraft] = useState("");
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState("");
  const [notice, setNotice] = useState("");
  const [previewOpen, setPreviewOpen] = useState(false);

  const me = useQuery({ queryKey: ["me"], queryFn: () => api.me() });
  const companies = useQuery({ queryKey: ["companies"], queryFn: () => api.companies() });
  const projects = useQuery({
    queryKey: ["projects", companyId],
    queryFn: () => api.projects(companyId),
    enabled: Boolean(companyId),
  });
  const tags = useQuery({
    queryKey: ["tags", companyId],
    queryFn: () => api.tags(companyId),
    enabled: Boolean(companyId),
  });
  const media = useQuery({
    queryKey: ["media", companyId, projectId, search],
    queryFn: () => api.mediaFiles(companyId, projectId, search),
    enabled: Boolean(companyId && projectId),
  });

  useEffect(() => {
    const available = companies.data?.items ?? [];
    if (!available.length) return;
    if (!available.some((company) => company.id === companyId)) {
      setCompanyId(available[0].id);
      setProjectId("");
    }
  }, [companies.data, companyId]);

  useEffect(() => {
    const available = projects.data?.items ?? [];
    if (!available.length) {
      setProjectId("");
      return;
    }
    if (!available.some((project) => project.id === projectId)) {
      setProjectId(available[0].id);
    }
  }, [projects.data, projectId]);

  useEffect(() => {
    if (companyId && projectId) {
      const target = `/companies/${companyId}/projects/${projectId}/catalog`;
      if (window.location.pathname !== target) navigate(target, { replace: true });
    }
  }, [companyId, navigate, projectId]);

  const selected = media.data?.items.find((item) => item.id === selectedId) ?? null;
  const totalBytes = (media.data?.items ?? []).reduce((sum, item) => sum + item.size_bytes, 0);
  const currentCompany = companies.data?.items.find((item) => item.id === companyId);

  const saveMedia = useMutation({
    mutationFn: (values: {
      display_name: string;
      description: string;
      observations: string;
    }) => {
      if (!selected) throw new Error("Selecione um arquivo.");
      return api.updateMediaFile(companyId, selected.id, {
        ...values,
        expected_version: selected.version,
      });
    },
    onSuccess: async () => {
      setNotice("Alterações salvas.");
      await queryClient.invalidateQueries({ queryKey: ["media", companyId, projectId] });
    },
  });

  const changeTag = useMutation({
    mutationFn: ({ tagId, checked }: { tagId: string; checked: boolean }) => {
      if (!selected) throw new Error("Selecione um arquivo.");
      return api.setTag(companyId, selected.id, tagId, checked);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["media", companyId, projectId] });
    },
  });

  const mediaAccess = useMutation({
    mutationFn: ({ item }: { item: MediaFile; action: "download" | "drive"; popup?: Window | null }) =>
      api.mediaPlayback(companyId, item.id),
    onSuccess: (session, variables) => {
      if (variables.action === "drive") {
        if (variables.popup) variables.popup.location.href = session.drive_url;
        else window.open(session.drive_url, "_blank", "noopener,noreferrer");
        return;
      }
      const link = document.createElement("a");
      link.href = session.download_url;
      document.body.appendChild(link);
      link.click();
      link.remove();
    },
    onError: (_error, variables) => variables.popup?.close(),
  });

  const error =
    companies.error || projects.error || media.error || saveMedia.error || changeTag.error || mediaAccess.error;

  return (
    <div className="app-frame">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">L</span>
          <div><strong>GERENCIADOR DE ÁUDIO VISUAL</strong><small>Acervo audiovisual</small></div>
        </div>
        <div className="session-area">
          <button className="ghost-button" type="button" onClick={() => navigate("/")}>
            <Icon name="grid" size={16} /> Empresas
          </button>
          <span className="online-dot" />
          <span>{currentCompany?.name ?? "Carregando empresa…"}</span>
          <button className="ghost-button" type="button" onClick={() => void auth.logout()}>
            Sair
          </button>
        </div>
      </header>

      <aside className="sidebar">
        <p className="sidebar-title">Ambiente de trabalho</p>
        <label>
          Empresa
          <select
            value={companyId}
            onChange={(event) => {
              setCompanyId(event.target.value);
              setProjectId("");
              setSelectedId("");
            }}
          >
            {(companies.data?.items ?? []).map((company) => (
              <option key={company.id} value={company.id}>{company.name}</option>
            ))}
          </select>
        </label>
        <label>
          Projeto
          <select value={projectId} onChange={(event) => setProjectId(event.target.value)}>
            {(projects.data?.items ?? []).map((project) => (
              <option key={project.id} value={project.id}>{project.name}</option>
            ))}
          </select>
        </label>
        <nav aria-label="Navegação principal">
          <a className="nav-item active" href="#catalogo"><span>▦</span> Catálogo</a>
          <a className="nav-item" href="#google-drive"><span>↑</span> Envios</a>
          <span className="nav-item disabled"><span>◎</span> Máquinas <small>em breve</small></span>
          <span className="nav-item disabled"><span>☰</span> Auditoria <small>em breve</small></span>
        </nav>
        <div className="user-card">
          <span className="avatar">{(currentCompany?.role ?? "U")[0]}</span>
          <div><strong>{currentCompany?.role ?? "Usuário"}</strong><small>{me.data?.id.slice(0, 8)}</small></div>
        </div>
      </aside>

      <main className="content" id="catalogo">
        <div className="page-heading">
          <div><span className="eyebrow">Projeto selecionado</span><h1>Catálogo de arquivos</h1></div>
          <span className="safe-badge">✓ Organização local protegida</span>
        </div>

        {error && <div className="alert error-message">{error.message}</div>}
        {notice && <div className="alert success-message">{notice}</div>}

        <DriveConnectionPanel
          api={api}
          companyId={companyId}
          projectId={projectId}
          isOwner={currentCompany?.role === "OWNER"}
        />

        <UploadBatchPanel
          api={api}
          companyId={companyId}
          projectId={projectId}
          projects={projects.data?.items ?? []}
        />

        <section className="summary-grid" aria-label="Resumo do catálogo">
          <article><span>Arquivos encontrados</span><strong>{media.data?.items.length ?? 0}</strong></article>
          <article><span>Volume catalogado</span><strong>{formatFileSize(totalBytes)}</strong></article>
          <article><span>Projeto</span><strong>{projects.data?.items.find((item) => item.id === projectId)?.name ?? "—"}</strong></article>
        </section>

        <section className="catalog-card">
          <form
            className="searchbar"
            onSubmit={(event) => {
              event.preventDefault();
              setSearch(searchDraft);
              setSelectedId("");
            }}
          >
            <input
              aria-label="Buscar arquivos"
              placeholder="Buscar por nome, descrição ou observação"
              value={searchDraft}
              onChange={(event) => setSearchDraft(event.target.value)}
            />
            <button className="primary-button" type="submit">Buscar</button>
          </form>

          {media.isLoading ? (
            <div className="empty-state">Carregando o catálogo…</div>
          ) : !projectId ? (
            <div className="empty-state">Selecione um projeto para visualizar seus arquivos.</div>
          ) : media.data?.items.length === 0 ? (
            <div className="empty-state"><strong>Nenhum arquivo encontrado</strong><span>Organize arquivos pelo agente local ou ajuste sua busca.</span></div>
          ) : (
            <MediaFileList
              items={media.data?.items ?? []}
              selectedId={selectedId}
              busyId={mediaAccess.isPending ? mediaAccess.variables?.item.id : undefined}
              onSelect={(item) => { setSelectedId(item.id); setNotice(""); }}
              onPreview={(item) => { setSelectedId(item.id); setPreviewOpen(true); }}
              onDownload={(item) => mediaAccess.mutate({ item, action: "download" })}
              onOpenDrive={(item) => {
                const popup = window.open("about:blank", "_blank");
                if (popup) popup.opener = null;
                mediaAccess.mutate({ item, action: "drive", popup });
              }}
            />
          )}
        </section>
      </main>

      {selected && (
        <MediaEditor
          media={selected}
          tags={tags.data?.items ?? []}
          busy={saveMedia.isPending || changeTag.isPending}
          onClose={() => { setSelectedId(""); setPreviewOpen(false); }}
          onPreview={() => setPreviewOpen(true)}
          onSave={(values) => saveMedia.mutate(values)}
          onTagChange={(tagId, checked) => changeTag.mutate({ tagId, checked })}
        />
      )}
      {selected && previewOpen && (
        <MediaPreview
          api={api}
          companyId={companyId}
          media={selected}
          onClose={() => setPreviewOpen(false)}
        />
      )}
    </div>
  );
}
