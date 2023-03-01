import React from 'react';
import { useParams, Redirect } from 'react-router-dom';
import { usePaymentVerificationPlanQuery } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

export function CashPlanVerificationRedirectPage(): React.ReactElement {
  const { id } = useParams();
  const { data, loading } = usePaymentVerificationPlanQuery({
    variables: { id },
  });
  const businessArea = useBusinessArea();
  if (loading) {
    return null;
  }
  return (
    <Redirect
      to={`/${businessArea}/payment-verification/${data.paymentVerificationPlan.id}`}
    />
  );
}
