import { api } from './api';

export const fetchTargetPopulations = async (
  businessAreaSlug: string,
  programId: string,
): Promise<any> => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/targeting/target-populations/`,
  );
  return response;
};
