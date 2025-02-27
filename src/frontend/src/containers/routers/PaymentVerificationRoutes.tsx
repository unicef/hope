import { useRoutes } from 'react-router-dom';
import { ReactElement } from 'react';
import PaymentPlanVerificationDetailsPage from '@containers/pages/payments/PaymentPlanVerificationDetailsPage';
import PaymentVerificationPage from '@containers/pages/payments/PaymentVerificationPage';
import VerificationPaymentDetailsPage from '@containers/pages/payments/VerificationPaymentDetailsPage';

export const PaymentVerificationRoutes = (): ReactElement => {
  const paymentVerificationRoutes = [
    {
      path: 'verification/payment/:id',
      element: <VerificationPaymentDetailsPage />,
    },
    {
      path: 'payment-verification',
      element: <PaymentVerificationPage />,
    },
    {
      path: 'payment-verification/payment-plan/:paymentPlanId',
      element: <PaymentPlanVerificationDetailsPage />,
    },
  ];

  return useRoutes(paymentVerificationRoutes);
};
