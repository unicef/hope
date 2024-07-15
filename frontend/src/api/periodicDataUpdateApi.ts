import { api } from './api';

export const fetchPeriodicDataUpdateTemplates = async (
  businessAreaSlug,
  programId,
  params = {},
) => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/`,
    params,
  );
  return response;
};

export const fetchPeriodicDataUpdateUpdates = async (
  businessAreaSlug,
  programId,
  params = {},
) => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-uploads/`,
    params,
  );
  return response;
};

export const fetchPeriodicDataUpdateTemplateDetails = async (
  businessAreaSlug,
  programId,
  templateId,
) => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/`,
  );
  return response;
};

export const exportPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  templateId: string,
): Promise<any> => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/export/`,
  );
  return response.data;
};

export const fetchPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  templateId: string,
): Promise<any> => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/download/`,
  );
  return response.data;
};

export const uploadPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  file: File,
  additionalParams: Record<string, any> = {},
) => {
  const formData = new FormData();
  formData.append('file', file);

  Object.keys(additionalParams).forEach((key) => {
    formData.append(key, additionalParams[key]);
  });

  const response = await api.post(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/`,
    formData,
  );

  return response;
};
