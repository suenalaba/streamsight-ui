const BASE_URL = 'http://127.0.0.1:8000';

export const getStatus = async () => {
  return fetch(`${BASE_URL}/`);
};