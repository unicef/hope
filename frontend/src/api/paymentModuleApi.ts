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
