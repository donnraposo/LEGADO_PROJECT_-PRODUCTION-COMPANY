import { describe, expect, it } from "vitest";

import { formatFileSize } from "./fileSize";

describe("formatFileSize", () => {
  it("mantém bytes pequenos legíveis", () => {
    expect(formatFileSize(900)).toBe("900 B");
  });

  it("converte arquivos grandes sem perder a unidade", () => {
    expect(formatFileSize(1536)).toBe("1,5 KB");
    expect(formatFileSize(5 * 1024 ** 3)).toBe("5 GB");
  });
});
