import { api } from './api';

export const fetchAreas = async (
  businessArea: string,
  queryParams: string,
): Promise<any> => {
  const response = await api.get(`${businessArea}/geo/areas/?${queryParams}`);
  return response;
};
