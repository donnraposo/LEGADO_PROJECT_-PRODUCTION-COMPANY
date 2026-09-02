import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

import type { BackendClient } from "../../shared/api/backendClient";
import type { Company } from "../../shared/api/types";
import { Icon } from "../../shared/ui/Icon";

interface ProjectModalProps {
  api: BackendClient;
  company: Company;
  onClose: () => void;
  onOpenProject: (projectId: string) => void;
}

export function ProjectModal({ api, company, onClose, onOpenProject }: ProjectModalProps) {
  const [search, setSearch] = useState("");
  const closeButton = useRef<HTMLButtonElement>(null);
  const projects = useQuery({
    queryKey: ["projects", company.id],
    queryFn: () => api.projects(company.id),
  });

  useEffect(() => {
    closeButton.current?.focus();
    const closeOnEscape = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [onClose]);

  const filtered = (projects.data?.items ?? []).filter((project) =>
    project.name.toLocaleLowerCase("pt-BR").includes(search.toLocaleLowerCase("pt-BR")),
  );

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section aria-labelledby="projects-title" aria-modal="true" className="project-modal" role="dialog">
        <header className="project-modal-header">
          <div className="modal-company-mark">{company.name[0]?.toUpperCase()}</div>
          <div><span className="eyebrow">Empresa selecionada</span><h2 id="projects-title">{company.name}</h2><p>Escolha um projeto para acessar produções e arquivos.</p></div>
          <button aria-label="Fechar projetos" className="icon-button" onClick={onClose} ref={closeButton} type="button"><Icon name="close" /></button>
        </header>

        <div className="modal-toolbar">
          <label className="search-field"><Icon name="search" /><span className="sr-only">Buscar projetos</span><input onChange={(event) => setSearch(event.target.value)} placeholder="Buscar projetos" value={search} /></label>
          <span>{filtered.length} {filtered.length === 1 ? "projeto" : "projetos"}</span>
        </div>

        <div className="project-grid">
          {projects.isLoading ? (
            Array.from({ length: 3 }).map((_, index) => <div className="project-skeleton" key={index} />)
          ) : projects.error ? (
            <div className="modal-empty error-message">{projects.error.message}</div>
          ) : filtered.length ? filtered.map((project, index) => (
            <button className={`project-card project-cover-${index % 4}`} key={project.id} onClick={() => onOpenProject(project.id)} type="button">
              <span className="project-cover"><span className="project-play">▶</span></span>
              <span className="project-card-body"><span className="eyebrow">Projeto audiovisual</span><strong>{project.name}</strong><small>Organizado por mês e data</small><span className="project-link">Abrir projeto <Icon name="chevron" size={16} /></span></span>
            </button>
          )) : (
            <div className="modal-empty"><Icon name="folder" size={28} /><strong>Nenhum projeto encontrado</strong><span>Ajuste a busca ou crie um projeto para esta empresa.</span></div>
          )}
        </div>
      </section>
    </div>
  );
}
