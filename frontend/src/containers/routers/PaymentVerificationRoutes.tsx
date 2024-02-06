import React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { CashPlanDetailsPage } from '../pages/payments/CashPlanDetailsPage';
import { CashPlanVerificationDetailsPage } from '../pages/payments/CashPlanVerificationDetailsPage';
import { CashPlanVerificationRedirectPage } from '../pages/payments/CashplanVerificationRedirectPage';
import { PaymentPlanVerificationDetailsPage } from '../pages/payments/PaymentPlanVerificationDetailsPage';
import { PaymentVerificationPage } from '../pages/payments/PaymentVerificationPage';
import { VerificationPaymentDetailsPage } from '../pages/payments/VerificationPaymentDetailsPage';
import { VerificationPaymentRecordDetailsPage } from '../pages/payments/VerificationPaymentRecordDetailsPage';

export function PaymentVerificationRoutes(): React.ReactElement {
  const { path } = useRouteMatch();

  const paymentVerificationRoutes = [
    {
      path: `${path}/cashplans/:id`,
      component: <CashPlanDetailsPage />,
    },
    {
      path: `${path}/verification/payment-record/:id`,
      component: <VerificationPaymentRecordDetailsPage />,
    },
    {
      path: `${path}/verification/payment/:id`,
      component: <VerificationPaymentDetailsPage />,
    },
    {
      path: `${path}/payment-verification`,
      component: <PaymentVerificationPage />,
      exact: true,
    },
    {
      path: `${path}/payment-verification/cash-plan/:id`,
      component: <CashPlanVerificationDetailsPage />,
    },
    {
      path: `${path}/payment-verification/payment-plan/:id`,
      component: <PaymentPlanVerificationDetailsPage />,
    },
    {
      path: `${path}/csh-payment-verification/:id`,
      component: <CashPlanVerificationRedirectPage />,
    },
  ];

  return (
    <Switch>
      {paymentVerificationRoutes.map((route) => (
        <SentryRoute key={route.path} path={route.path} exact={route.exact}>
          {route.component}
        </SentryRoute>
      ))}
    </Switch>
  );
}
