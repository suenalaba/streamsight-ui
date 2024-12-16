import { CreateStreamRequest, CreateStreamResponse } from './types';

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
