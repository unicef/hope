import { fetchSupportingDocument } from '@api/paymentModuleApi';
import { useMutation } from '@tanstack/react-query';

export const useDownloadSupportingDocument = () => {
  return useMutation({
    mutationFn: ({
      businessAreaSlug: mutationBusinessAreaSlug,
      programId: mutationProgramId,
      paymentPlanId: mutationPaymentPlanId,
      fileId: mutationFileId,
      fileName: mutationFileName,
    }: {
      businessAreaSlug: string;
      programId: string;
      paymentPlanId: string;
      fileId: string;
      fileName: string;
    }) => {
      return fetchSupportingDocument(
        mutationBusinessAreaSlug,
        mutationProgramId,
        mutationPaymentPlanId,
        mutationFileId,
        mutationFileName,
      );
    },
  });
};
