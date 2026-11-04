import { useParams, useRoutes, Navigate } from 'react-router-dom';
import FollowUpPaymentListDetailsPage from '@containers/pages/paymentmodule/FollowUpPaymentListDetailsPage';
import PaymentDetailsPage from '@containers/pages/paymentmodule/PaymentDetailsPage';
import CreatePaymentListPage from '@containers/pages/paymentmodule/ProgramCycle/CreatePaymentListPage';
import PaymentListDetailsPage from '@containers/pages/paymentmodule/ProgramCycle/PaymentListDetails/PaymentListDetailsPage';
import ProgramCycleDetailsPage from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsPage';
import ProgramCyclePage from '@containers/pages/paymentmodule/ProgramCycle/ProgramCyclePage';
import PaymentPlansPage from '@containers/pages/paymentmodule/PaymentPlans/PaymentPlansPage';
import PaymentPlanDetailsPage from '@containers/pages/paymentmodule/PaymentPlans/PaymentPlanDetailsPage';
import FollowUpInstructionListPage from '@containers/pages/paymentmodule/FollowUpInstructionListPage';
import FollowUpInstructionDetailsPage from '@containers/pages/paymentmodule/FollowUpInstructionDetailsPage';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { ReactElement } from 'react';

const LegacyPaymentPlanRedirect = (): ReactElement => {
  const { paymentPlanId } = useParams<{ paymentPlanId: string }>();
  const { baseUrl } = useBaseUrl();
  return (
    <Navigate
      to={`/${baseUrl}/payment-module/payment-plans/${paymentPlanId}`}
      replace
    />
  );
};

export const PaymentModuleRoutes = (): ReactElement => {
  const children = [
    {
      path: 'payment-lists',
      children: [
        {
          path: '',
          element: <Navigate to="../payment-plans" replace />,
        },
        {
          path: ':paymentListId',
          children: [
            {
              path: '',
              element: <PaymentListDetailsPage />,
            },
          ],
        },
      ],
    },
    {
      path: 'followup-payment-lists/:paymentListId',
      children: [
        {
          path: '',
          element: <FollowUpPaymentListDetailsPage />,
        },
      ],
    },
    {
      path: 'top-up-payment-lists/:paymentListId',
      children: [
        {
          path: '',
          element: <FollowUpPaymentListDetailsPage />,
        },
      ],
    },
    {
      path: 'payments/:paymentId',
      element: <PaymentDetailsPage />,
    },
    {
      path: 'payment-plans',
      children: [
        {
          path: '',
          element: <PaymentPlansPage />,
        },
        {
          path: ':paymentPlanId',
          children: [
            {
              path: '',
              element: <PaymentPlanDetailsPage />,
            },
          ],
        },
      ],
    },
    // Payment plan links sent before the rename used the groups path.
    {
      path: 'groups',
      element: <Navigate to="../payment-plans" replace />,
    },
    {
      path: 'groups/:paymentPlanId',
      element: <LegacyPaymentPlanRedirect />,
    },
    {
      path: 'follow-up-instructions',
      children: [
        {
          path: '',
          element: <FollowUpInstructionListPage />,
        },
        {
          path: ':instructionId',
          element: <FollowUpInstructionDetailsPage />,
        },
      ],
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
              path: 'payment-lists',
              children: [
                {
                  path: 'new-plan',
                  element: <CreatePaymentListPage />,
                },
                {
                  path: ':paymentListId',
                  children: [
                    {
                      path: '',
                      element: <PaymentListDetailsPage />,
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
