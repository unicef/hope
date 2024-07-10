import {
  fetchPeriodicDataUpdateTemplate,
  exportPeriodicDataUpdateTemplate,
} from '@api/periodicDataUpdate';
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
    }) =>
      fetchPeriodicDataUpdateTemplate(
        mutationBusinessAreaSlug,
        mutationProgramId,
        mutationTemplateId,
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['fetchPeriodicDataUpdateTemplates'],
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
        queryKey: ['fetchPeriodicDataUpdateTemplates'],
      });
    },
  });
};
