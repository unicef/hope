import { useRoutes, Navigate } from 'react-router-dom';
import type { ReactElement } from 'react';
import PaymentListVerificationDetailsPage from '@containers/pages/payments/PaymentListVerificationDetailsPage';
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
          path: 'payment-list/:paymentListId',
          element: <PaymentListVerificationDetailsPage />,
        },
        {
          path: 'payment-list/:paymentListId/verification/payment/:id',
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
