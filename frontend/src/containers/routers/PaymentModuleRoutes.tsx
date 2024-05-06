import * as React from 'react';
import { useRoutes } from 'react-router-dom';
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
import { SetUpFollowUpFspPage } from '../pages/paymentmodule/SetUpFollowUpFspPage';

export const PaymentModuleRoutes = (): React.ReactElement => {
  const paymentModuleRoutes = [
    {
      path: 'payment-module/new-plan',
      element: <CreatePaymentPlanPage />,
    },
    {
      path: 'payment-module',
      element: <PaymentModulePage />,
    },
    {
      path: 'payment-module/followup-payment-plans/:id/edit',
      element: <EditFollowUpPaymentPlanPage />,
    },
    {
      path: 'payment-module/followup-payment-plans/:id/setup-fsp/edit',
      element: <EditFollowUpSetUpFspPage />,
    },
    {
      path: 'payment-module/followup-payment-plans/:id/setup-fsp/create',
      element: <SetUpFollowUpFspPage />,
    },
    {
      path: 'payment-module/payment-plans/:id/setup-fsp/edit',
      element: <EditSetUpFspPage />,
    },
    {
      path: 'payment-module/payment-plans/:id/edit',
      element: <EditPaymentPlanPage />,
    },
    {
      path: 'payment-module/payments/:id',
      element: <PaymentDetailsPage />,
    },
    {
      path: 'payment-module/payment-plans/:id/setup-fsp/create',
      element: <SetUpFspPage />,
    },
    {
      path: 'payment-module/payment-plans/:id',
      element: <PaymentPlanDetailsPage />,
    },
    {
      path: 'payment-module/followup-payment-plans/:id',
      element: <FollowUpPaymentPlanDetailsPage />,
    },
  ];

  return useRoutes(paymentModuleRoutes);
};
