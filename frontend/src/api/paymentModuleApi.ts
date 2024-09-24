import { api } from './api';

export const fetchPaymentPlansManagerial = async (
  businessAreaSlug,
  params = {},
) => {
  const paramsWithNoLimit = {
    ...params,
    limit: 10000,
    offset: 0,
  };
  const response = await api.get(
    `${businessAreaSlug}/payments/payment-plans-managerial/`,
    paramsWithNoLimit,
  );
  return response;
};

export const bulkActionPaymentPlansManagerial = async (
  businessAreaSlug,
  ids,
  action,
  comment,
) => {
  const payload: { ids: typeof ids; action: typeof action; comment?: string } =
    {
      ids,
      action,
    };

  if (comment) {
    payload.comment = comment;
  }

  const response = await api.post(
    `${businessAreaSlug}/payments/payment-plans-managerial/bulk-action/`,
    payload,
  );
  return response.data;
};

export const deleteSupportingDocument = async (
  businessArea: string,
  programId: string,
  paymentPlanId: string,
  fileId: string,
) => {
  try {
    await api.delete(
      `/${businessArea}/programs/${programId}/payment-plans/${paymentPlanId}/supporting-documents/${fileId}/`,
    );
    return { success: true };
  } catch (error: any) {
    const errorMessage = error?.message || 'An unknown error occurred';
    throw new Error(`Failed to delete supporting document: ${errorMessage}`);
  }
};

export const uploadSupportingDocument = async (
  businessArea: string,
  programId: string,
  paymentPlanId: string,
  file: File,
  title: string,
) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);

  try {
    await api.post(
      `${businessArea}/programs/${programId}/payment-plans/${paymentPlanId}/supporting-documents-upload/`,
      formData,
    );
    return { success: true };
  } catch (error) {
    throw new Error(`Failed to upload supporting document: ${error.message}`);
  }
};
