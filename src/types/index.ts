// Organization related types
export interface Organization {
  id: string;
  name: string;
  createdAt: string;
}

// User related types
export interface User {
  id: string;
  email: string;
  name: string;
  organizationId: string;
}

// API Token related types
export interface ApiToken {
  id: string;
  name: string;
  token: string;
  createdAt: string;
  expiresAt: string | null;
  lastUsedAt: string | null;
}

export interface CreateApiTokenRequest {
  name: string;
  expiresInDays: number | null;
}

export interface CreateApiTokenResponse {
  token: ApiToken;
}