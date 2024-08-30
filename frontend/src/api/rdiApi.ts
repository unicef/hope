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
