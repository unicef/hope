import { api, handleApiResponse, Params } from './api';

export const exportPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  templateId: string,
): Promise<any> => {
  return handleApiResponse(
    api.post(
      `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/export/`,
      {},
    ),
  );
};

export const fetchPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  templateId: string,
): Promise<any> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/download/`,
      {},
      `Periodic_Data_Update_Template_${templateId}`,
    ),
  );
};

export const uploadPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  file: File,
  additionalParams: Params = {},
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  Object.keys(additionalParams).forEach((key) => {
    formData.append(key, additionalParams[key]);
  });

  return handleApiResponse(
    api.post(
      `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-uploads/upload/`,
      formData,
    ),
  );
};

export const createPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  roundsData: Params,
  filters: Params | null,
): Promise<any> => {
  const payload = {
    rounds_data: roundsData,
    filters: filters,
  };

  return handleApiResponse(
    api.post(
      `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/`,
      payload,
    ),
  );
};
