import { api } from './api';
import { PaginatedAreaList } from '@restgenerated/models/PaginatedAreaList';

export const fetchAreas = async (
  businessArea: string,
  queryParams: string,
): Promise<PaginatedAreaList> => {
  const response = await api.get(`${businessArea}/geo/areas/?${queryParams}`);
  return response;
};
