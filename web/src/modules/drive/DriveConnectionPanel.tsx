import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { BackendClient } from "../../shared/api/backendClient";

interface DriveConnectionPanelProps {
  api: BackendClient;
  companyId: string;
  isOwner: boolean;
}

export function DriveConnectionPanel({ api, companyId, isOwner }: DriveConnectionPanelProps) {
  const queryClient = useQueryClient();
  const account = useQuery({
    queryKey: ["drive-account", companyId],
    queryFn: () => api.driveAccount(companyId),
    enabled: Boolean(companyId),
  });
  const connect = useMutation({
    mutationFn: () => api.startDriveAuthorization(companyId),
    onSuccess: ({ authorization_url }) => window.location.assign(authorization_url),
  });
  const disconnect = useMutation({
    mutationFn: () => api.disconnectDrive(companyId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["drive-account", companyId] });
    },
  });
  const oauthResult = new URLSearchParams(window.location.search).get("drive");
  const error = account.error || connect.error || disconnect.error;

  return (
    <section className="drive-card" id="google-drive" aria-labelledby="drive-title">
      <div>
        <span className="eyebrow">Destino dos envios</span>
        <h2 id="drive-title">Google Drive</h2>
        {account.isLoading ? (
          <p>Verificando a conexão…</p>
        ) : account.data?.connected ? (
          <p><strong>Conta conectada:</strong> {account.data.account_email}</p>
        ) : (
          <p>Conecte uma conta para preparar os próximos lotes de envio.</p>
        )}
        {oauthResult === "connected" && <p className="inline-success">Conta conectada com sucesso.</p>}
        {oauthResult === "error" && <p className="inline-error">Não foi possível concluir a conexão. Tente novamente.</p>}
        {error && <p className="inline-error">{error.message}</p>}
      </div>
      {isOwner ? (
        account.data?.connected ? (
          <button className="ghost-button dark" type="button" disabled={disconnect.isPending} onClick={() => disconnect.mutate()}>
            {disconnect.isPending ? "Desconectando…" : "Desconectar"}
          </button>
        ) : (
          <button className="primary-button" type="button" disabled={!companyId || connect.isPending} onClick={() => connect.mutate()}>
            {connect.isPending ? "Abrindo Google…" : "Conectar conta Google"}
          </button>
        )
      ) : (
        <span className="status-pill">Somente proprietário</span>
      )}
    </section>
  );
}
