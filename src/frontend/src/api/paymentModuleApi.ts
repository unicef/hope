import { api } from './api';
import { PaymentPlan } from '@restgenerated/models/PaymentPlan';

export const fetchPaymentPlansManagerial = async (
  businessAreaSlug,
  params = {},
): Promise<PaymentPlan[]> => {
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

interface BulkActionPaymentPlansManagerialProps {
  businessAreaSlug: string;
  ids: string[];
  action: string;
  comment: string;
}

export const bulkActionPaymentPlansManagerial = async ({
  businessAreaSlug,
  ids,
  action,
  comment,
}: BulkActionPaymentPlansManagerialProps) => {
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
