import * as React from 'react';
import { useRoutes, useLocation } from 'react-router-dom';
import { SentryRoute } from '@components/core/SentryRoute';
import { CashPlanDetailsPage } from '../pages/payments/CashPlanDetailsPage';
import { CashPlanVerificationDetailsPage } from '../pages/payments/CashPlanVerificationDetailsPage';
import { CashPlanVerificationRedirectPage } from '../pages/payments/CashplanVerificationRedirectPage';
import { PaymentPlanVerificationDetailsPage } from '../pages/payments/PaymentPlanVerificationDetailsPage';
import { PaymentVerificationPage } from '../pages/payments/PaymentVerificationPage';
import { VerificationPaymentDetailsPage } from '../pages/payments/VerificationPaymentDetailsPage';
import { VerificationPaymentRecordDetailsPage } from '../pages/payments/VerificationPaymentRecordDetailsPage';

export const PaymentVerificationRoutes = (): React.ReactElement => {
  const location = useLocation();
  const path = location.pathname;

  const paymentVerificationRoutes = [
    {
      path: `${path}/cashplans/:id`,
      element: (
        <SentryRoute
          path={`${path}/cashplans/:id`}
          element={<CashPlanDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/verification/payment-record/:id`,
      element: (
        <SentryRoute
          path={`${path}/verification/payment-record/:id`}
          element={<VerificationPaymentRecordDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/verification/payment/:id`,
      element: (
        <SentryRoute
          path={`${path}/verification/payment/:id`}
          element={<VerificationPaymentDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/payment-verification`,
      element: (
        <SentryRoute
          path={`${path}/payment-verification`}
          element={<PaymentVerificationPage />}
        />
      ),
    },
    {
      path: `${path}/payment-verification/cash-plan/:id`,
      element: (
        <SentryRoute
          path={`${path}/payment-verification/cash-plan/:id`}
          element={<CashPlanVerificationDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/payment-verification/payment-plan/:id`,
      element: (
        <SentryRoute
          path={`${path}/payment-verification/payment-plan/:id`}
          element={<PaymentPlanVerificationDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/csh-payment-verification/:id`,
      element: (
        <SentryRoute
          path={`${path}/csh-payment-verification/:id`}
          element={<CashPlanVerificationRedirectPage />}
        />
      ),
    },
  ];

  const routes = useRoutes(paymentVerificationRoutes);

  return routes;
};
