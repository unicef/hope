import React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { CreatePaymentPlanPage } from '../pages/paymentmodule/CreatePaymentPlanPage';
import { EditFollowUpPaymentPlanPage } from '../pages/paymentmodule/EditFollowUpPaymentPlanPage';
import { EditFollowUpSetUpFspPage } from '../pages/paymentmodule/EditFollowUpSetUpFspPage';
import { EditPaymentPlanPage } from '../pages/paymentmodule/EditPaymentPlanPage';
import { EditSetUpFspPage } from '../pages/paymentmodule/EditSetUpFspPage';
import { FollowUpPaymentPlanDetailsPage } from '../pages/paymentmodule/FollowUpPaymentPlanDetailsPage';
import { PaymentDetailsPage } from '../pages/paymentmodule/PaymentDetailsPage';
import { PaymentModulePage } from '../pages/paymentmodule/PaymentModulePage';
import { PaymentPlanDetailsPage } from '../pages/paymentmodule/PaymentPlanDetailsPage';
import { SetUpFspPage } from '../pages/paymentmodule/SetUpFspPage';

export function PaymentModuleRoutes(): React.ReactElement {
  const { path } = useRouteMatch();

  const paymentModuleRoutes = [
    {
      path: `${path}/payment-module/new-plan`,
      component: <CreatePaymentPlanPage />,
    },
    {
      path: `${path}/payment-module`,
      component: <PaymentModulePage />,
      exact: true,
    },

    {
      path: `${path}/payment-module/followup-payment-plans/:id/edit`,
      component: <EditFollowUpPaymentPlanPage />,
    },

    {
      path: `${path}/payment-module/followup-payment-plans/:id/setup-fsp/edit`,
      component: <EditFollowUpSetUpFspPage />,
    },
    {
      path: `${path}/payment-module/payment-plans/:id/setup-fsp/create`,
      component: <SetUpFspPage />,
    },
    {
      path: `${path}/payment-module/payment-plans/:id/setup-fsp/edit`,
      component: <EditSetUpFspPage />,
    },

    {
      path: `${path}/payment-module/payment-plans/:id/edit`,
      component: <EditPaymentPlanPage />,
    },

    {
      path: `${path}/payment-module/payments/:id`,
      component: <PaymentDetailsPage />,
    },
    {
      path: `${path}/payment-module/payment-plans/:id`,
      component: <PaymentPlanDetailsPage />,
    },
    {
      path: `${path}/payment-module/followup-payment-plans/:id`,
      component: <FollowUpPaymentPlanDetailsPage />,
    },
  ];

  return (
    <Switch>
      {paymentModuleRoutes.map((route) => (
        <SentryRoute key={route.path} path={route.path} exact={route.exact}>
          {route.component}
        </SentryRoute>
      ))}
    </Switch>
  );
}
