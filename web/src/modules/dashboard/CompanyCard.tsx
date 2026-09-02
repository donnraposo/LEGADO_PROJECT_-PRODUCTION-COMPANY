import type { Company } from "../../shared/api/types";
import { Icon } from "../../shared/ui/Icon";

interface CompanyCardProps {
  company: Company;
  featured?: boolean;
  index: number;
  onOpen: (company: Company) => void;
}

const scenes = ["production", "coast", "studio", "city", "camera", "ocean"];

export function CompanyCard({ company, featured = false, index, onOpen }: CompanyCardProps) {
  const initials = company.name.split(/\s+/).slice(0, 2).map((word) => word[0]).join("").toUpperCase();

  return (
    <button
      className={`company-card company-scene-${scenes[index % scenes.length]} ${featured ? "featured" : ""}`}
      onClick={() => onOpen(company)}
      type="button"
    >
      <span className="company-card-shade" />
      <span className="company-card-menu" aria-hidden="true">•••</span>
      <span className="company-monogram">{initials}</span>
      <span className="company-card-content">
        <strong>{company.name}</strong>
        <span className="company-meta"><Icon name="folder" size={15} /> Ver projetos</span>
        <span className="company-activity">Ambiente {company.role === "OWNER" ? "administrado por você" : "compartilhado"}</span>
        <span className="company-card-footer">
          <span className="avatar-stack" aria-label="Equipe vinculada"><i>{initials[0]}</i><i>+2</i></span>
          <span className="operational-status"><i /> Ativa</span>
        </span>
      </span>
    </button>
  );
}
