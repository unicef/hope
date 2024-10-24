import { api } from './api';


export const fetchTargetPopulations = async (
  businessAreaSlug: string,
  programId: string,
  params = {},
): Promise<any> => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/targeting/target-populations/`,
    params,
  );
  return response;
};
