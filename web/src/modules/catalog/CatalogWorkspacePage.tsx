import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useAuth } from "../authentication/AuthProvider";
import { BackendClient } from "../../shared/api/backendClient";
import type { MediaFile } from "../../shared/api/types";
import { formatFileSize } from "../../shared/format/fileSize";
import { MediaEditor } from "./MediaEditor";

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

  const error =
    companies.error || projects.error || media.error || saveMedia.error || changeTag.error;

  return (
    <div className="app-frame">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">L</span>
          <div><strong>LEGADO</strong><small>Acervo audiovisual</small></div>
        </div>
        <div className="session-area">
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
          <span className="nav-item disabled"><span>↑</span> Envios <small>em breve</small></span>
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
            <div className="media-list">
              {(media.data?.items ?? []).map((item: MediaFile) => (
                <button
                  type="button"
                  className={`media-row ${selectedId === item.id ? "selected" : ""}`}
                  key={item.id}
                  onClick={() => { setSelectedId(item.id); setNotice(""); }}
                >
                  <span className="file-icon">{item.media_type.startsWith("video") ? "▶" : "▣"}</span>
                  <span className="file-main"><strong>{item.display_name}</strong><small>{item.original_name}</small></span>
                  <span>{formatFileSize(item.size_bytes)}</span>
                  <span className="tag-preview">{item.tags.map((tag) => tag.name).join(" · ") || "Sem tags"}</span>
                  <span className="status-pill">{item.status}</span>
                </button>
              ))}
            </div>
          )}
        </section>
      </main>

      {selected && (
        <MediaEditor
          media={selected}
          tags={tags.data?.items ?? []}
          busy={saveMedia.isPending || changeTag.isPending}
          onClose={() => setSelectedId("")}
          onSave={(values) => saveMedia.mutate(values)}
          onTagChange={(tagId, checked) => changeTag.mutate({ tagId, checked })}
        />
      )}
    </div>
  );
}
