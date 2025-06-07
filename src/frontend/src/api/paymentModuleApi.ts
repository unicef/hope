import { api, handleApiResponse, handleMutationError } from './api';

interface BulkActionPaymentPlansManagerialProps {
  businessAreaSlug: string;
  ids: string[];
  action: string;
  comment?: string;
}

export const bulkActionPaymentPlansManagerial = async ({
  businessAreaSlug,
  ids,
  action,
  comment,
}: BulkActionPaymentPlansManagerialProps) => {
  const payload: { ids: string[]; action: string; comment?: string } = {
    ids,
    action,
  };

  if (comment) {
    payload.comment = comment;
  }

  try {
    const response = await api.post(
      `${businessAreaSlug}/payments/payment-plans-managerial/bulk-action/`,
      payload,
    );
    return response.data;
  } catch (error) {
    handleMutationError(error, 'perform bulk action on payment plans');
  }
};

export const deleteSupportingDocument = async (
  businessArea: string,
  programId: string,
  paymentPlanId: string,
  fileId: string,
): Promise<{ success: boolean }> => {
  try {
    await api.delete(
      `${businessArea}/programs/${programId}/payment-plans/${paymentPlanId}/supporting-documents/${fileId}/`,
    );
    return { success: true };
  } catch (error) {
    handleMutationError(error, 'delete supporting document');
  }
};

export const uploadSupportingDocument = async (
  businessArea: string,
  programId: string,
  paymentPlanId: string,
  file: File,
  title: string,
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);

  try {
    const response = await api.post(
      `${businessArea}/programs/${programId}/payment-plans/${paymentPlanId}/supporting-documents/`,
      formData,
    );
    return response.data;
  } catch (error) {
    handleMutationError(error, 'upload supporting document');
  }
};

export const fetchSupportingDocument = async (
  businessAreaSlug: string,
  programId: string,
  paymentPlanId: string,
  fileId: string,
  fileName: string,
): Promise<any> => {
  return handleApiResponse(
    api.get(
      `${businessAreaSlug}/programs/${programId}/payment-plans/${paymentPlanId}/supporting-documents/${fileId}/download/`,
      {},
      fileName,
    ),
  );
};
