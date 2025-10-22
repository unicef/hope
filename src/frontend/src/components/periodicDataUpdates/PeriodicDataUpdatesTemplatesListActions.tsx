import { useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';

export const useDownloadPeriodicDataUpdateTemplate = () => {
  return useMutation({
    mutationFn: ({
      businessAreaSlug,
      programSlug,
      templateId,
    }: {
      businessAreaSlug: string;
      programSlug: string;
      templateId: number;
    }) =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateTemplatesDownloadRetrieve(
        {
          businessAreaSlug,
          programSlug,
          id: templateId,
        },
      ),
  });
};

export const useExportPeriodicDataUpdateTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      businessAreaSlug,
      programSlug,
      templateId,
    }: {
      businessAreaSlug: string;
      programSlug: string;
      templateId: number;
    }) =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateTemplatesExportCreate(
        {
          businessAreaSlug,
          programSlug,
          id: templateId,
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['periodicDataUpdateTemplates'],
      });
    },
  });
};

export const useUploadPeriodicDataUpdateTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      businessAreaSlug,
      programSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      programSlug: string;
      requestBody: any; // Should match PeriodicDataUpdateTemplateCreate
    }) =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateTemplatesCreate({
        businessAreaSlug,
        programSlug,
        requestBody,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['periodicDataUpdateUploads'],
      });
    },
  });
};
