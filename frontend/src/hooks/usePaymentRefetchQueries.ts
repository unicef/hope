import { DocumentNode } from 'graphql';
import {
  AllPaymentVerificationsDocument,
  CashPlanDocument,
} from '../__generated__/graphql';
import { useBusinessArea } from './useBusinessArea';

export const usePaymentRefetchQueries = (
  cashPlanId: string,
): (() => [
  {
    query: DocumentNode;
    variables: { cashPlanId: string; businessArea: string };
  },
  { query: DocumentNode; variables: { id: string } },
]) => {
  const businessArea = useBusinessArea();
  return () => [
    {
      query: AllPaymentVerificationsDocument,
      variables: { cashPlanId, businessArea },
    },
    {
      query: CashPlanDocument,
      variables: { id: cashPlanId },
    },
  ];
};
