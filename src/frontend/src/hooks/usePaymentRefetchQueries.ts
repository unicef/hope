import { DocumentNode } from 'graphql';
import {
  AllPaymentVerificationsDocument,
  CashPlanDocument,
  PaymentPlanDocument,
} from '@generated/graphql';
import { useBaseUrl } from './useBaseUrl';

export const usePaymentRefetchQueries = (
  paymentPlanId: string,
): (() => [
    {
      query: DocumentNode;
      variables: { paymentPlanId: string; businessArea: string };
    },
    { query: DocumentNode; variables: { id: string } },
  ]) => {
  const { businessArea } = useBaseUrl();
  const planType = atob(paymentPlanId).split(':')[0];

  return () => [
    {
      query: AllPaymentVerificationsDocument,
      variables: {
        paymentPlanId,
        businessArea,
        paymentVerificationPlan: null,
        first: 5,
        orderBy: null,
        search: null,
        status: null,
        verificationChannel: null,
      },
    },
    {
      query:
        planType === 'PaymentPlanNode' ? PaymentPlanDocument : CashPlanDocument,
      variables: { id: paymentPlanId },
    },
  ];
};
