import { api } from './api';
import { PaginatedPeriodicDataUpdateTemplateListList } from '@restgenerated/models/PaginatedPeriodicDataUpdateTemplateListList';
import { PeriodicDataUpdateUploadList } from '@restgenerated/models/PeriodicDataUpdateUploadList';
import { PeriodicDataUpdateTemplateDetail } from '@restgenerated/models/PeriodicDataUpdateTemplateDetail';
import { PeriodicDataUpdateUploadDetail } from '@restgenerated/models/PeriodicDataUpdateUploadDetail';
import { PaginatedPeriodicFieldList } from '@restgenerated/models/PaginatedPeriodicFieldList';

export const fetchPeriodicDataUpdateTemplates = async (
  businessAreaSlug: string,
  programId: string,
  params = {},
): Promise<PaginatedPeriodicDataUpdateTemplateListList> => {
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
): Promise<PeriodicDataUpdateUploadList> => {
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
): Promise<PeriodicDataUpdateTemplateDetail> => {
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
  const response = await api.post(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/export/`,
    {},
  );
  return response;
};

export const fetchPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  templateId: string,
): Promise<any> => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/download/`,
  );
  return response;
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
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-uploads/upload/`,
    formData,
  );
  return response;
};

export const fetchPeriodicDataUpdateUploadDetails = async (
  businessAreaSlug,
  programId,
  uploadId,
): Promise<PeriodicDataUpdateUploadDetail> => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-uploads/${uploadId}/`,
  );
  return response;
};

export const createPeriodicDataUpdateTemplate = async (
  businessAreaSlug: string,
  programId: string,
  roundsData: Record<string, any>,
  filters: Record<string, any> | null,
) => {
  const payload = {
    rounds_data: roundsData,
    filters: filters,
  };

  const response = await api.post(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/`,
    payload,
  );
  return response;
};

export const fetchPeriodicFields = async (
  businessAreaSlug: string,
  programId: string,
  params = {},
): Promise<PaginatedPeriodicFieldList> => {
  const response = await api.get(
    `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-fields/`,
    params,
  );
  return response;
};
