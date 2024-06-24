import { api } from './api';

export const fetchPeriodicDataUpdateTemplates = async (
  businessAreaSlug,
  programId,
  params = {},
) => {
  const response = await api.get(
    `/api/rest/${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/`,
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
    `/api/rest/${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/`,
  );
  return response;
};

export const exportPeriodicDataUpdateTemplate = async (
  businessAreaSlug,
  programId,
  templateId,
) => {
  const response = await api.post(
    `/api/rest/${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/export/`,
  );
  return response.data;
};

export const downloadPeriodicDataUpdateTemplate = async (
  businessAreaSlug,
  programId,
  templateId,
) => {
  const response = await api.get(
    `/api/rest/${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/download/`,
  );
  return response.data;
};
