import { api, handleApiResponse } from './api';
import { PaginatedAreaList } from '@restgenerated/models/PaginatedAreaList';

export const fetchAreas = async (
  businessArea: string,
  queryParams: string,
): Promise<PaginatedAreaList> => {
  return handleApiResponse(
    api.get(`${businessArea}/geo/areas/?${queryParams}`),
  );
};
