import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { keycloak } from "./keycloak";

interface AuthState {
  accessToken: () => Promise<string>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [failure, setFailure] = useState("");

  useEffect(() => {
    let active = true;
    keycloak
      .init({ onLoad: "login-required", pkceMethod: "S256", checkLoginIframe: false })
      .then((authenticated) => {
        if (!authenticated) return keycloak.login();
        if (active) setReady(true);
      })
      .catch(() => {
        if (active) setFailure("Não foi possível iniciar a autenticação.");
      });
    return () => {
      active = false;
    };
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      accessToken: async () => {
        await keycloak.updateToken(30);
        if (!keycloak.token) throw new Error("Sessão expirada.");
        return keycloak.token;
      },
      logout: async () => {
        await keycloak.logout({ redirectUri: window.location.origin });
      },
    }),
    [],
  );

  if (failure) return <div className="full-page-message error-message">{failure}</div>;
  if (!ready) return <div className="full-page-message">Preparando seu ambiente seguro…</div>;
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const value = useContext(AuthContext);
  if (!value) throw new Error("AuthProvider ausente.");
  return value;
}
