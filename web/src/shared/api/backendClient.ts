import type { Collection, Company, CurrentUser, MediaFile, Project, Tag } from "./types";

type TokenProvider = () => Promise<string>;

export class BackendClient {
  constructor(private readonly tokenProvider: TokenProvider) {}

  me() {
    return this.request<CurrentUser>("/api/v1/me");
  }

  companies() {
    return this.request<Collection<Company>>("/api/v1/companies");
  }

  projects(companyId: string) {
    return this.request<Collection<Project>>("/api/v1/projects", {}, companyId);
  }

  tags(companyId: string) {
    return this.request<Collection<Tag>>("/api/v1/tags", {}, companyId);
  }

  mediaFiles(companyId: string, projectId: string, search = "") {
    const query = new URLSearchParams({ project_id: projectId });
    if (search.trim()) query.set("q", search.trim());
    return this.request<Collection<MediaFile>>(
      `/api/v1/media-files?${query.toString()}`,
      {},
      companyId,
    );
  }

  updateMediaFile(
    companyId: string,
    mediaFileId: string,
    body: Pick<MediaFile, "display_name" | "description" | "observations"> & {
      expected_version: number;
    },
  ) {
    return this.request<MediaFile>(
      `/api/v1/media-files/${mediaFileId}`,
      { method: "PATCH", body: JSON.stringify(body) },
      companyId,
    );
  }

  setTag(companyId: string, mediaFileId: string, tagId: string, selected: boolean) {
    return this.request<void>(
      `/api/v1/media-files/${mediaFileId}/tags/${tagId}`,
      { method: selected ? "PUT" : "DELETE" },
      companyId,
    );
  }

  private async request<T>(path: string, init: RequestInit = {}, companyId?: string): Promise<T> {
    const accessToken = await this.tokenProvider();
    const headers = new Headers(init.headers);
    headers.set("Authorization", `Bearer ${accessToken}`);
    headers.set("Accept", "application/json");
    if (init.body) headers.set("Content-Type", "application/json");
    if (companyId) headers.set("X-Company-ID", companyId);
    const response = await fetch(path, { ...init, headers });
    if (response.status === 204) return undefined as T;
    if (!response.ok) throw new Error(await this.safeError(response));
    return (await response.json()) as T;
  }

  private async safeError(response: Response): Promise<string> {
    try {
      const data = (await response.json()) as { detail?: string; title?: string };
      return data.detail || data.title || `Falha na operação (${response.status}).`;
    } catch {
      return `Falha na operação (${response.status}).`;
    }
  }
}
