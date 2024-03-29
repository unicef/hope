import { api } from './api';

export const fetchPaymentPlansManagerial = async (
  businessAreaSlug,
  params = {},
) => {
  const response = await api.get(
    `/api/rest/${businessAreaSlug}/payments/payment-plans-managerial/`,
    params,
  );
  return response;
};

export const bulkActionPaymentPlansManagerial = async (
  businessAreaSlug,
  ids,
  action,
  comment,
) => {
  const response = await api.post(
    `/api/rest/${businessAreaSlug}/payments/payment-plans-managerial/bulk-action/`,
    {
      ids,
      action,
      comment,
    },
  );
  return response.data;
};
