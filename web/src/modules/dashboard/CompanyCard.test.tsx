import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CompanyCard } from "./CompanyCard";

const company = {
  id: "company-1",
  name: "Aurora Filmes",
  role: "OWNER" as const,
  version: 1,
};

describe("CompanyCard", () => {
  it("apresenta a empresa e abre seus projetos", () => {
    const onOpen = vi.fn();
    render(<CompanyCard company={company} featured index={0} onOpen={onOpen} />);

    expect(screen.getByText("Aurora Filmes")).toBeInTheDocument();
    expect(screen.getByText("Ver projetos")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Aurora Filmes/i }));
    expect(onOpen).toHaveBeenCalledWith(company);
  });
});
