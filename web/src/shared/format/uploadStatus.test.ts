import { describe, expect, it } from "vitest";

import { formatUploadStatus } from "./uploadStatus";

describe("formatUploadStatus", () => {
  it.each([
    ["CREATED", "CRIADO"],
    ["PENDING", "PENDENTE"],
    ["READY", "PRONTO"],
    ["RUNNING", "EM ANDAMENTO"],
    ["UPLOADING", "ENVIANDO"],
    ["PAUSE_REQUESTED", "PAUSA SOLICITADA"],
    ["PAUSED", "PAUSADO"],
    ["CANCEL_REQUESTED", "CANCELAMENTO SOLICITADO"],
    ["VERIFYING", "VERIFICANDO"],
    ["INTERRUPTED", "INTERROMPIDO"],
    ["SUCCEEDED", "CONCLUÍDO"],
    ["FAILED", "FALHOU"],
    ["CANCELLED", "CANCELADO"],
    ["ACTIVE", "ATIVO"],
    ["EXPIRED", "EXPIRADO"],
  ])("traduz %s", (status, expected) => {
    expect(formatUploadStatus(status)).toBe(expected);
  });

  it("não expõe um valor técnico desconhecido", () => {
    expect(formatUploadStatus("NEW_INTERNAL_STATUS")).toBe("STATUS DESCONHECIDO");
  });
});
