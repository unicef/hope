import { api } from './api';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';

export const fetchTargetPopulations = async (
  businessAreaSlug: string,
  programId: string,
  params = {},
): Promise<TargetPopulationList> => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/targeting/target-populations/`,
    params,
  );
  return response;
};
