import React from 'react';
import { useParams, Redirect } from 'react-router-dom';
import { useCashPlanPaymentVerificationQuery } from '../../__generated__/graphql';
import { useBusinessArea } from '../../hooks/useBusinessArea';

export function CashplanVerificationRedirectPage(): React.ReactElement {
  const { id } = useParams();
  const { data, loading } = useCashPlanPaymentVerificationQuery({
    variables: { id },
  });
  const businessArea = useBusinessArea();
  if (loading) {
    return null;
  }
  return (
    <Redirect
      to={`/${businessArea}/payment-verification/${data.cashPlanPaymentVerification.cashPlan.id}`}
    />
  );
}
