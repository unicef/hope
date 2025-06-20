import { api, handleApiResponse, handleMutationError } from './api';
import { RegistrationDataImportList } from '@restgenerated/models/RegistrationDataImportList';

export const fetchRegistrationDataImports = async (
  businessAreaSlug: string,
  programId: string,
  params = {},
): Promise<RegistrationDataImportList> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/registration-data/registration-data-imports/`,
      params,
    ),
  );
};

export const runDeduplicationDataImports = async (
  businessAreaSlug: string,
  programId: string,
): Promise<any> => {
  try {
    const response = await api.post(
      `${businessAreaSlug}/programs/${programId}/registration-data/registration-data-imports/run-deduplication/`,
      {},
    );
    return response.data;
  } catch (error) {
    handleMutationError(error, 'run deduplication data imports');
  }
};
