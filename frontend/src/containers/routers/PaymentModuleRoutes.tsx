import * as React from 'react';
import { Route, useLocation, useRoutes } from 'react-router-dom';
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

export const PaymentModuleRoutes = (): React.ReactElement => {
  const location = useLocation();
  const path = location.pathname;

  const paymentModuleRoutes = [
    {
      path: `${path}/payment-module/new-plan`,
      element: (
        <Route
          path={`${path}/payment-module/new-plan`}
          element={<CreatePaymentPlanPage />}
        />
      ),
    },
    {
      path: `${path}/payment-module`,
      element: (
        <Route
          path={`${path}/payment-module`}
          element={<PaymentModulePage />}
        />
      ),
    },
    {
      path: `${path}/payment-module/followup-payment-plans/:id/edit`,
      element: (
        <Route
          path={`${path}/payment-module/followup-payment-plans/:id/edit`}
          element={<EditFollowUpPaymentPlanPage />}
        />
      ),
    },
    {
      path: `${path}/payment-module/followup-payment-plans/:id/setup-fsp/edit`,
      element: (
        <Route
          path={`${path}/payment-module/followup-payment-plans/:id/setup-fsp/edit`}
          element={<EditFollowUpSetUpFspPage />}
        />
      ),
    },
    {
      path: `${path}/payment-module/payment-plans/:id/setup-fsp/create`,
      element: (
        <Route
          path={`${path}/payment-module/payment-plans/:id/setup-fsp/create`}
          element={<SetUpFspPage />}
        />
      ),
    },
    {
      path: `${path}/payment-module/payment-plans/:id/setup-fsp/edit`,
      element: (
        <Route
          path={`${path}/payment-module/payment-plans/:id/setup-fsp/edit`}
          element={<EditSetUpFspPage />}
        />
      ),
    },
    {
      path: `${path}/payment-module/payment-plans/:id/edit`,
      element: (
        <Route
          path={`${path}/payment-module/payment-plans/:id/edit`}
          element={<EditPaymentPlanPage />}
        />
      ),
    },
    {
      path: `${path}/payment-module/payments/:id`,
      element: (
        <Route
          path={`${path}/payment-module/payments/:id`}
          element={<PaymentDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/payment-module/payment-plans/:id`,
      element: (
        <Route
          path={`${path}/payment-module/payment-plans/:id`}
          element={<PaymentPlanDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/payment-module/followup-payment-plans/:id`,
      element: (
        <Route
          path={`${path}/payment-module/followup-payment-plans/:id`}
          element={<FollowUpPaymentPlanDetailsPage />}
        />
      ),
    },
  ];

  return useRoutes(paymentModuleRoutes);
};
