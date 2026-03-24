import { useRoutes, Navigate } from 'react-router-dom';
import EditFollowUpPaymentPlanPage from '@containers/pages/paymentmodule/EditFollowUpPaymentPlanPage';
import EditPaymentPlanPage from '@containers/pages/paymentmodule/EditPaymentPlanPage';
import FollowUpPaymentPlanDetailsPage from '@containers/pages/paymentmodule/FollowUpPaymentPlanDetailsPage';
import PaymentDetailsPage from '@containers/pages/paymentmodule/PaymentDetailsPage';
import PaymentModulePage from '@containers/pages/paymentmodule/PaymentModulePage';
import CreatePaymentPlanPage from '@containers/pages/paymentmodule/ProgramCycle/CreatePaymentPlanPage';
import PaymentPlanDetailsPage from '@containers/pages/paymentmodule/ProgramCycle/PaymentPlanDetails/PaymentPlanDetailsPage';
import ProgramCycleDetailsPage from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsPage';
import ProgramCyclePage from '@containers/pages/paymentmodule/ProgramCycle/ProgramCyclePage';
import { ReactElement } from 'react';

export const PaymentModuleRoutes = (): ReactElement => {
  const children = [
    {
      path: 'payment-plans',
      children: [
        {
          path: '',
          element: <PaymentModulePage />,
        },
        {
          path: ':paymentPlanId',
          children: [
            {
              path: '',
              element: <PaymentPlanDetailsPage />,
            },
            {
              path: 'edit',
              element: <EditPaymentPlanPage />,
            },
          ],
        },
      ],
    },
    {
      path: 'followup-payment-plans/:paymentPlanId',
      children: [
        {
          path: '',
          element: <FollowUpPaymentPlanDetailsPage />,
        },
        {
          path: 'edit',
          element: <EditFollowUpPaymentPlanPage />,
        },
      ],
    },
    {
      path: 'payments/:paymentId',
      element: <PaymentDetailsPage />,
    },
    {
      path: '*',
      element: <Navigate to="/404" replace />,
    },
    {
      path: 'program-cycles',
      children: [
        {
          path: '',
          element: <ProgramCyclePage />,
        },
        {
          path: ':programCycleId',
          children: [
            {
              path: '',
              element: <ProgramCycleDetailsPage />,
            },
            {
              path: 'payment-plans',
              children: [
                {
                  path: 'new-plan',
                  element: <CreatePaymentPlanPage />,
                },
                {
                  path: ':paymentPlanId',
                  children: [
                    {
                      path: '',
                      element: <PaymentPlanDetailsPage />,
                    },
                    {
                      path: 'edit',
                      element: <EditPaymentPlanPage />,
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    },
  ];

  return useRoutes([
    {
      path: 'payment-module',
      children,
    },
  ]);
};
