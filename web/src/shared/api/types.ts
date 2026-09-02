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
export type UploadBatch = components["schemas"]["UploadBatch"];
export type UploadBatchDetail = components["schemas"]["UploadBatchDetail"];
export type CreateUploadBatch = components["schemas"]["CreateUploadBatchRequest"];

export interface Collection<T> {
  items: T[];
  next_cursor?: string | null;
}

export interface DriveAccount {
  connected: boolean;
  account_email: string | null;
  connected_at: string | null;
}

export interface DriveAuthorization {
  authorization_url: string;
}

export type MediaPlaybackSession = components["schemas"]["MediaPlaybackSession"];

export interface DriveFolderTree {
  path: string;
  folders: {
    originais: string;
    previews: string;
    entregas: string;
  };
}
