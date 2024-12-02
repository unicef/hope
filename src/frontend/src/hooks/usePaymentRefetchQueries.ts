import { DocumentNode } from 'graphql';
import {
  AllPaymentVerificationsDocument,
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
      query: PaymentPlanDocument,
      variables: { id: paymentPlanId },
    },
  ];
};
