import { fetchSupportingDocument } from '@api/paymentModuleApi';
import { useMutation } from '@tanstack/react-query';

export const useDownloadSupportingDocument = () => {
  return useMutation({
    mutationFn: ({
      businessAreaSlug: mutationBusinessAreaSlug,
      programId: mutationProgramId,
      paymentPlanId: mutationPaymentPlanId,
      fileId: mutationFileId,
    }: {
      businessAreaSlug: string;
      programId: string;
      paymentPlanId: string;
      fileId: string;
    }) => {
      return fetchSupportingDocument(
        mutationBusinessAreaSlug,
        mutationProgramId,
        mutationPaymentPlanId,
        mutationFileId,
      );
    },
    onSuccess: (data) => {
      if (data.url) {
        window.open(data.url);
      }
    },
  });
};
