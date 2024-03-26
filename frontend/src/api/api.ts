import axios from 'axios';

export const api = axios.create({
  baseURL: '/api/rest/',
  headers: {
    Accept: 'application/json',
  },
});

api.get = async function (url, params = {}) {
  try {
    const response = await axios.get(url, { params });
    return response.data;
  } catch (error) {
    console.error(`Error fetching data from ${url}:`, error);
    throw error;
  }
};

api.post = async function (url, data = {} as any) {
  try {
    const response = await axios.post(url, data);
    return response.data;
  } catch (error) {
    console.error(`Error posting data to ${url}:`, error);
    throw error;
  }
};
