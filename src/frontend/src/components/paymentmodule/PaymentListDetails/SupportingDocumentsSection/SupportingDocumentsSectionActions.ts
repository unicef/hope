import { fetchSupportingDocument } from '@api/paymentModuleApi';
import { useMutation } from '@tanstack/react-query';

export const useDownloadSupportingDocument = () => {
  return useMutation({
    mutationFn: ({
      businessAreaSlug: mutationBusinessAreaSlug,
      programId: mutationProgramId,
      ownerPath: mutationOwnerPath,
      fileId: mutationFileId,
      fileName: mutationFileName,
    }: {
      businessAreaSlug: string;
      programId: string;
      ownerPath: string;
      fileId: string;
      fileName: string;
    }) => {
      return fetchSupportingDocument(
        mutationBusinessAreaSlug,
        mutationProgramId,
        mutationOwnerPath,
        mutationFileId,
        mutationFileName,
      );
    },
  });
};
