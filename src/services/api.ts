import { Organization, User, ApiToken, CreateApiTokenRequest, CreateApiTokenResponse } from '../types';

const API_BASE_URL = 'https://api.tembo.io/v1';

// Helper function for API requests
const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('auth_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
};

// Organization related API calls
export const getOrganization = async (): Promise<Organization> => {
  return fetchWithAuth('/organization');
};

// User related API calls
export const getCurrentUser = async (): Promise<User> => {
  return fetchWithAuth('/user');
};

// API Token related API calls
export const getApiTokens = async (): Promise<ApiToken[]> => {
  return fetchWithAuth('/tokens');
};

export const createApiToken = async (data: CreateApiTokenRequest): Promise<CreateApiTokenResponse> => {
  return fetchWithAuth('/tokens', {
    method: 'POST',
    body: JSON.stringify(data)
  });
};

export const deleteApiToken = async (tokenId: string): Promise<void> => {
  await fetchWithAuth(`/tokens/${tokenId}`, {
    method: 'DELETE'
  });
};