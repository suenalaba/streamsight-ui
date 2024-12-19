import { AlgorithmUuidToState, CreateStreamRequest, CreateStreamResponse, RegisterAlgorithmRequest, RegisterAlgorithmResponse, StreamSettings, StreamStatus } from './types';

const BASE_URL = 'http://127.0.0.1:8000';

export const getStatus = async () => {
  return fetch(`${BASE_URL}/`);
};

export const createStream = async (data: CreateStreamRequest): Promise<CreateStreamResponse> => {
    const response = await fetch(`${BASE_URL}/streams`, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    return json;
};

export const getStreamSettings = async (streamId: string): Promise<StreamSettings> => {
  const response = await fetch(`${BASE_URL}/streams/${streamId}/settings`);
  
  if (!response.ok) {
    throw new Error(`Response status: ${response.status}`);
  }

  const json = await response.json();
  return json;
}

export const registerAlgorithm = async (streamId: string, data: RegisterAlgorithmRequest): Promise<RegisterAlgorithmResponse> => {
  const response = await fetch(`${BASE_URL}/streams/${streamId}/algorithms`, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Response status: ${response.status}`);
  }

  const json = await response.json();
  return json;
}

export const getAlgorithmStates = async (streamId: string): Promise<AlgorithmUuidToState[]> => {
  const response = await fetch(`${BASE_URL}/streams/${streamId}/algorithms/state`);

  if (!response.ok) {
    throw new Error(`Response status: ${response.status}`);
  }

  const json = await response.json();
  return json;
}

export const getStreamStatus = async (streamId: string): Promise<StreamStatus> => {
  const response = await fetch(`${BASE_URL}/streams/${streamId}/status`);

  if (!response.ok) {
    throw new Error(`Response status: ${response.status}`);
  }

  const json = await response.json();
  return json;
}

export const getUserStreamStatuses = async (): Promise<StreamStatus[]> => {
  const response = await fetch(`${BASE_URL}/streams/user`);

  if (!response.ok) {
    throw new Error(`Response status: ${response.status}`);
  }

  const json = await response.json();
  return json;
}
