import { useRoutes, Navigate } from 'react-router-dom';
import { ReactElement } from 'react';
import PaymentPlanVerificationDetailsPage from '@containers/pages/payments/PaymentPlanVerificationDetailsPage';
import PaymentVerificationPage from '@containers/pages/payments/PaymentVerificationPage';
import VerificationPaymentDetailsPage from '@containers/pages/payments/VerificationPaymentDetailsPage';

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
          path: 'payment-plan/:paymentPlanId',
          element: <PaymentPlanVerificationDetailsPage />,
        },
        {
          path: 'payment-plan/:paymentPlanId/verification/payment/:id',
          element: <VerificationPaymentDetailsPage />,
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
