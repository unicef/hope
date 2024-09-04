import { api } from './api';

export const fetchRegistrationDataImports = async (
  businessAreaSlug: string,
  programId: string,
  params = {},
): Promise<any> => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/registration-data/registration-data-imports/`,
    params,
  );
  return response;
};

export const runDeduplicationDataImports = async (
  businessAreaSlug: string,
  programId: string,
): Promise<any> => {
  return api.post(
    `${businessAreaSlug}/programs/${programId}/registration-data/registration-data-imports/run-deduplication/`,
    {},
  );
};
