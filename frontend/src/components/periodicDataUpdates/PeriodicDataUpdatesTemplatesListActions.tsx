import {
  fetchPeriodicDataUpdateTemplate,
  exportPeriodicDataUpdateTemplate,
  uploadPeriodicDataUpdateTemplate,
} from '@api/periodicDataUpdateApi';
import { useMutation, useQueryClient } from '@tanstack/react-query';

export const useDownloadPeriodicDataUpdateTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      businessAreaSlug: mutationBusinessAreaSlug,
      programId: mutationProgramId,
      templateId: mutationTemplateId,
    }: {
      businessAreaSlug: string;
      programId: string;
      templateId: string;
    }) =>{
      return fetchPeriodicDataUpdateTemplate(
        mutationBusinessAreaSlug,
        mutationProgramId,
        mutationTemplateId,
      )
    },
    onSuccess: (data) => {
      console.log('data', data)
      if (data.url) {
        window.open(data.url);
      }
      queryClient.invalidateQueries({
        queryKey: ['periodicDataUpdateTemplates'],
      });
    },
  });
};

export const useExportPeriodicDataUpdateTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      businessAreaSlug: mutationBusinessAreaSlug,
      programId: mutationProgramId,
      templateId: mutationTemplateId,
    }: {
      businessAreaSlug: string;
      programId: string;
      templateId: string;
    }) =>
      exportPeriodicDataUpdateTemplate(
        mutationBusinessAreaSlug,
        mutationProgramId,
        mutationTemplateId,
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
      programId,
      file,
      additionalParams,
    }: {
      businessAreaSlug: string;
      programId: string;
      file: File;
      additionalParams?: Record<string, any>;
    }) =>
      uploadPeriodicDataUpdateTemplate(
        businessAreaSlug,
        programId,
        file,
        additionalParams,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['periodicDataUpdateTemplates'],
      });
    },
  });
};
