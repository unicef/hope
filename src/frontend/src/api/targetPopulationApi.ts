import { api, handleApiResponse } from './api';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';

export const fetchTargetPopulations = async (
  businessAreaSlug: string,
  programId: string,
  params = {},
): Promise<TargetPopulationList> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/targeting/target-populations/`,
      params,
    ),
  );
};
