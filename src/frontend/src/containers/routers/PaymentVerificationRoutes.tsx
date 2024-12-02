import { useRoutes } from 'react-router-dom';
import { PaymentPlanVerificationDetailsPage } from '../pages/payments/PaymentPlanVerificationDetailsPage';
import { PaymentVerificationPage } from '../pages/payments/PaymentVerificationPage';
import { VerificationPaymentDetailsPage } from '../pages/payments/VerificationPaymentDetailsPage';
import { ReactElement } from 'react';

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
