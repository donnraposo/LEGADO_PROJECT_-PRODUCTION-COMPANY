import type { components } from "./schema";

export type CurrentUser = components["schemas"]["CurrentUser"];
export type Company = components["schemas"]["CompanyMembership"];

export interface Project {
  id: string;
  client_id: string;
  name: string;
}

export type Tag = components["schemas"]["Tag"];
export type MediaFile = components["schemas"]["MediaFile"];

export interface Collection<T> {
  items: T[];
  next_cursor?: string | null;
}
