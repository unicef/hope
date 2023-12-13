import React from 'react';
import { useParams, Redirect } from 'react-router-dom';
import { usePaymentVerificationPlanQuery } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

export function CashPlanVerificationRedirectPage(): React.ReactElement {
  const { id } = useParams();
  const { data, loading } = usePaymentVerificationPlanQuery({
    variables: { id },
  });
  const { baseUrl } = useBaseUrl();
  if (loading) {
    return null;
  }
  return (
    <Redirect
      to={`/${baseUrl}/payment-verification/${data.paymentVerificationPlan.id}`}
    />
  );
}
