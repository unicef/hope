import { UseMutationOptions } from '@tanstack/react-query';
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
  businessAreaSlug,
  programId,
  templateId,
) => {
  const response = await api.post(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/export/`,
  );
  return response.data;
};

export const downloadPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  templateId: string,
): Promise<any> => {
  // Consider using a more specific type instead of any if possible
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/download/`,
  );
  return response.data;
};

// Use the function within useMutation
const businessAreaSlug = 'yourBusinessAreaSlug'; // Define these variables as needed
const programId = 'yourProgramId';

const mutationOptions: UseMutationOptions<any, Error, string> = {
  onSuccess: () => {
    // Handle success
  },
  onError: (error: Error) => {
    // Handle error
  },
};

const { mutate: downloadTemplate } = useMutation(async (templateId: string) => {
  return downloadPeriodicDataUpdateTemplate(
    businessAreaSlug,
    programId,
    templateId,
  );
}, mutationOptions);
