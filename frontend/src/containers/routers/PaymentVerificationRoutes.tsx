import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { CashPlanDetailsPage } from '../pages/payments/CashPlanDetailsPage';
import { CashPlanVerificationDetailsPage } from '../pages/payments/CashPlanVerificationDetailsPage';
import { CashPlanVerificationRedirectPage } from '../pages/payments/CashplanVerificationRedirectPage';
import { PaymentPlanVerificationDetailsPage } from '../pages/payments/PaymentPlanVerificationDetailsPage';
import { PaymentVerificationPage } from '../pages/payments/PaymentVerificationPage';
import { VerificationPaymentDetailsPage } from '../pages/payments/VerificationPaymentDetailsPage';
import { VerificationPaymentRecordDetailsPage } from '../pages/payments/VerificationPaymentRecordDetailsPage';

export const PaymentVerificationRoutes = (): React.ReactElement => {
  const paymentVerificationRoutes = [
    {
      path: 'cashplans/:id',
      element: <CashPlanDetailsPage />,
    },
    {
      path: 'verification/payment-record/:id',
      element: <VerificationPaymentRecordDetailsPage />,
    },
    {
      path: 'verification/payment/:id',
      element: <VerificationPaymentDetailsPage />,
    },
    {
      path: 'payment-verification',
      element: <PaymentVerificationPage />,
    },
    {
      path: 'payment-verification/cash-plan/:id',
      element: <CashPlanVerificationDetailsPage />,
    },
    {
      path: 'payment-verification/payment-plan/:id',
      element: <PaymentPlanVerificationDetailsPage />,
    },
    {
      path: 'csh-payment-verification/:id',
      element: <CashPlanVerificationRedirectPage />,
    },
  ];

  return useRoutes(paymentVerificationRoutes);
};
