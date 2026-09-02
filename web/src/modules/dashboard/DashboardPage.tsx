import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { BackendClient } from "../../shared/api/backendClient";
import type { Company } from "../../shared/api/types";
import { Icon } from "../../shared/ui/Icon";
import { useAuth } from "../authentication/AuthProvider";
import { CompanyCard } from "./CompanyCard";
import { ProjectModal } from "./ProjectModal";

export function DashboardPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const api = useMemo(() => new BackendClient(auth.accessToken), [auth.accessToken]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [search, setSearch] = useState("");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const companies = useQuery({ queryKey: ["companies"], queryFn: () => api.companies() });
  const me = useQuery({ queryKey: ["me"], queryFn: () => api.me() });
  const visible = (companies.data?.items ?? []).filter((company) => company.name.toLocaleLowerCase("pt-BR").includes(search.toLocaleLowerCase("pt-BR")));
  const featured = visible.slice(0, 3);

  const openProject = (projectId: string) => {
    if (!selectedCompany) return;
    navigate(`/companies/${selectedCompany.id}/projects/${projectId}/catalog`);
  };

  return (
    <div className={`ocean-shell ${mobileNavOpen ? "nav-open" : ""}`}>
      <header className="dashboard-topbar">
        <button aria-label="Abrir menu" className="mobile-menu-button" onClick={() => setMobileNavOpen((current) => !current)} type="button"><Icon name="menu" /></button>
        <div className="brand"><span className="brand-mark">L</span><div><strong>LEGADO</strong><small>Produção audiovisual</small></div></div>
        <label className="global-search"><Icon name="search" /><span className="sr-only">Busca global</span><input onChange={(event) => setSearch(event.target.value)} placeholder="Buscar empresas…" value={search} /></label>
        <button className="primary-button new-project-button" disabled title="Criação de projetos em breve" type="button"><Icon name="plus" /> Novo projeto</button>
        <button aria-label="Sair" className="profile-button" onClick={() => void auth.logout()} type="button"><span>{me.data?.id.slice(0, 2).toUpperCase() ?? "US"}</span><Icon name="logout" size={16} /></button>
      </header>

      <aside className="dashboard-sidebar">
        <nav aria-label="Navegação principal">
          <a className="nav-item active" href="#visao-geral"><Icon name="home" /> Visão geral</a>
          <a className="nav-item" href="#empresas"><Icon name="building" /> Empresas</a>
          <a className="nav-item" href="#projetos"><Icon name="grid" /> Projetos</a>
          <a className="nav-item" href="#acervo"><Icon name="archive" /> Acervo</a>
          <a className="nav-item" href="#envios"><Icon name="send" /> Envios</a>
        </nav>
        <div className="storage-card"><span>Armazenamento</span><strong>Ambiente protegido</strong><div><i /></div><small>Google Drive conectado por empresa</small></div>
      </aside>

      <main className="dashboard-content" id="visao-geral">
        <div className="dashboard-heading"><div><span className="eyebrow">Central de produção</span><h1>Bom dia</h1><p>Continue de onde sua equipe parou.</p></div><span className="secure-label">● Operação segura</span></div>

        {companies.error && <div className="alert error-message">{companies.error.message}</div>}
        {companies.isLoading ? <div className="dashboard-loading">Carregando seus ambientes…</div> : visible.length ? <>
          <section className="company-section" id="empresas"><div className="section-heading"><div><span className="eyebrow">Acesso rápido</span><h2>Empresas em destaque</h2></div><button className="text-button" type="button">Ver todas <Icon name="chevron" size={15} /></button></div><div className="featured-company-grid">{featured.map((company, index) => <CompanyCard company={company} featured index={index} key={company.id} onOpen={setSelectedCompany} />)}</div></section>
          <section className="company-section"><div className="section-heading"><div><span className="eyebrow">Seus ambientes</span><h2>Todas as empresas</h2></div><span className="result-count">{visible.length} cadastradas</span></div><div className="company-grid">{visible.map((company, index) => <CompanyCard company={company} index={index + 2} key={company.id} onOpen={setSelectedCompany} />)}</div></section>
        </> : <div className="dashboard-empty"><Icon name="building" size={32} /><strong>{search ? "Nenhuma empresa encontrada" : "Nenhuma empresa disponível"}</strong><span>{search ? "Tente buscar por outro nome." : "As empresas vinculadas à sua conta aparecerão aqui."}</span></div>}
      </main>

      {selectedCompany && <ProjectModal api={api} company={selectedCompany} onClose={() => setSelectedCompany(null)} onOpenProject={openProject} />}
    </div>
  );
}
