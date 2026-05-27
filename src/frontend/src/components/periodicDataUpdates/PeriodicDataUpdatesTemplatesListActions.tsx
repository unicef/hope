import { useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';

export const useExportPeriodicDataUpdateTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      businessAreaSlug,
      programCode,
      templateId,
    }: {
      businessAreaSlug: string;
      programCode: string;
      templateId: number;
    }) =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateTemplatesExportCreate(
        {
          businessAreaSlug,
          programCode,
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
      programCode,
      requestBody,
    }: {
      businessAreaSlug: string;
      programCode: string;
      requestBody: any; // Should match PeriodicDataUpdateTemplateCreate
    }) =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateTemplatesCreate({
        businessAreaSlug,
        programCode,
        requestBody,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['periodicDataUpdateUploads'],
      });
    },
  });
};
