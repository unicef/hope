import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePaymentVerificationPlanQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';

export const CashPlanVerificationRedirectPage: React.FC = () => {
  const { id } = useParams();
  const { data, loading } = usePaymentVerificationPlanQuery({
    variables: { id },
  });
  const { baseUrl } = useBaseUrl();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && data) {
      navigate(
        `/${baseUrl}/payment-verification/${data.paymentVerificationPlan.id}`,
      );
    }
  }, [loading, data, navigate, baseUrl]);

  if (loading) {
    return null;
  }

  return null;
};
