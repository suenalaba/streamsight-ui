import { createClient } from '../utils/supabase/client';
import { BASE_URL } from './constants';
import { CreateStreamRequest, CreateStreamResponse, GetAllAlgorithmStateResponse, Metrics, RegisterAlgorithmRequest, RegisterAlgorithmResponse, StartStreamResponse, StreamSettings, StreamStatus } from './types';

const getAccessToken = async (): Promise<string | null> => {
  const supabase = createClient()
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || null;
};

const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = await getAccessToken();

  // if (!token) {
  //   throw new Error('User is not authenticated');
  // }

  const headers = {
    ...options.headers,
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
};

export const isUserAllowedToAccessStream = async (streamId: string): Promise<boolean> => {
  return fetchWithAuth(`${BASE_URL}/streams/${streamId}/check_access`, { method: 'GET'});
}

export const isUserAuthenticated = async (): Promise<boolean> => {
  const token = await getAccessToken();
  return !!token;
}

export const getHeroes = async () => {
  return fetchWithAuth(`${BASE_URL}/authentication/get_heroes`);
}

export const getStatus = async () => {
  return fetch(`${BASE_URL}/`);
};

export const createStream = async (data: CreateStreamRequest): Promise<CreateStreamResponse> => {
  return fetchWithAuth(`${BASE_URL}/streams`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
};

export const getStreamStatus = async (streamId: string): Promise<StreamStatus> => {
  return fetchWithAuth(`${BASE_URL}/streams/${streamId}/status`, { method: 'GET'});
}

export const getUserStreamStatuses = async (): Promise<StreamStatus[]> => {
  return fetchWithAuth(`${BASE_URL}/streams/user`, { method: 'GET'});
}

export const getStreamSettings = async (streamId: string): Promise<StreamSettings> => {
  return fetchWithAuth(`${BASE_URL}/streams/${streamId}/settings`, { method: 'GET'});
}

export const startStream = async (streamId: string): Promise<StartStreamResponse> => {
  return fetchWithAuth(`${BASE_URL}/streams/${streamId}/start`, {
    method: 'POST',
  });
}

export const registerAlgorithm = async (streamId: string, data: RegisterAlgorithmRequest): Promise<RegisterAlgorithmResponse> => {
  return fetchWithAuth(`${BASE_URL}/streams/${streamId}/algorithms`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
}

export const getAlgorithmStates = async (streamId: string): Promise<GetAllAlgorithmStateResponse> => {
  return fetchWithAuth(`${BASE_URL}/streams/${streamId}/algorithms/state`, { method: 'GET'});
}

export const getMetrics = async (streamId: string): Promise<Metrics> => {
  return fetchWithAuth(`${BASE_URL}/streams/${streamId}/metrics`, { method: 'GET'});
}

export const getMetricsList = async (): Promise<string[]> => {
  return fetchWithAuth(`${BASE_URL}/metrics`, { method: 'GET'});
}