import { useParams, useRoutes, Navigate } from 'react-router-dom';
import type { ReactElement } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import PaymentListVerificationDetailsPage from '@containers/pages/payments/PaymentListVerificationDetailsPage';
import PaymentVerificationPage from '@containers/pages/payments/PaymentVerificationPage';
import VerificationPaymentDetailsPage from '@containers/pages/payments/VerificationPaymentDetailsPage';

const LegacyPaymentPlanVerificationRedirect = (): ReactElement => {
  const { paymentPlanId, id } = useParams<{
    paymentPlanId: string;
    id: string;
  }>();
  const { baseUrl } = useBaseUrl();
  const paymentPath = id ? `/verification/payment/${id}` : '';

  return (
    <Navigate
      to={`/${baseUrl}/payment-verification/payment-list/${paymentPlanId}${paymentPath}`}
      replace
    />
  );
};

export const PaymentVerificationRoutes = (): ReactElement => {
  const paymentVerificationRoutes = [
    {
      path: 'payment-verification',
      children: [
        {
          path: '',
          element: <PaymentVerificationPage />,
        },
        {
          path: 'payment-list/:paymentListId',
          element: <PaymentListVerificationDetailsPage />,
        },
        {
          path: 'payment-plan/:paymentPlanId',
          element: <LegacyPaymentPlanVerificationRedirect />,
        },
        {
          path: 'payment-list/:paymentListId/verification/payment/:id',
          element: <VerificationPaymentDetailsPage />,
        },
        {
          path: 'payment-plan/:paymentPlanId/verification/payment/:id',
          element: <LegacyPaymentPlanVerificationRedirect />,
        },
        {
          path: '*',
          element: <Navigate to="/404" replace />,
        },
      ],
    },
  ];

  return useRoutes(paymentVerificationRoutes);
};
