import { api, handleApiResponse, Params } from './api';
import { PaginatedPeriodicDataUpdateTemplateListList } from '@restgenerated/models/PaginatedPeriodicDataUpdateTemplateListList';
import { PeriodicDataUpdateUploadList } from '@restgenerated/models/PeriodicDataUpdateUploadList';
import { PeriodicDataUpdateTemplateDetail } from '@restgenerated/models/PeriodicDataUpdateTemplateDetail';
import { PeriodicDataUpdateUploadDetail } from '@restgenerated/models/PeriodicDataUpdateUploadDetail';
import { PaginatedPeriodicFieldList } from '@restgenerated/models/PaginatedPeriodicFieldList';

export const fetchPeriodicDataUpdateTemplates = async (
  businessAreaSlug: string,
  programId: string,
  params: Params = {},
): Promise<PaginatedPeriodicDataUpdateTemplateListList> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/`,
      params,
    ),
  );
};

export const fetchPeriodicDataUpdateUpdates = async (
  businessAreaSlug: string,
  programId: string,
  params: Params = {},
): Promise<PeriodicDataUpdateUploadList> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-uploads/`,
      params,
    ),
  );
};

export const fetchPeriodicDataUpdateTemplateDetails = async (
  businessAreaSlug: string,
  programId: string,
  templateId: string,
): Promise<PeriodicDataUpdateTemplateDetail> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-templates/${templateId}/`,
    ),
  );
};

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

export const fetchPeriodicDataUpdateUploadDetails = async (
  businessAreaSlug: string,
  programId: string,
  uploadId: string,
): Promise<PeriodicDataUpdateUploadDetail> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-data-update-uploads/${uploadId}/`,
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

export const fetchPeriodicFields = async (
  businessAreaSlug: string,
  programId: string,
  params: Params = {},
): Promise<PaginatedPeriodicFieldList> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/periodic-data-update/periodic-fields/`,
      params,
    ),
  );
};
