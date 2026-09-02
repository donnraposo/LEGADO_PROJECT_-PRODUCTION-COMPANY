import { Navigate, Route, Routes } from "react-router-dom";

import { CatalogWorkspacePage } from "../modules/catalog/CatalogWorkspacePage";
import { DashboardPage } from "../modules/dashboard/DashboardPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route
        path="/companies/:companyId/projects/:projectId/catalog"
        element={<CatalogWorkspacePage />}
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
