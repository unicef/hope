import { useRoutes } from 'react-router-dom';
import { EditFollowUpPaymentPlanPage } from '../pages/paymentmodule/EditFollowUpPaymentPlanPage';
import { EditPaymentPlanPage } from '../pages/paymentmodule/EditPaymentPlanPage';
import { FollowUpPaymentPlanDetailsPage } from '../pages/paymentmodule/FollowUpPaymentPlanDetailsPage';
import { PaymentDetailsPage } from '../pages/paymentmodule/PaymentDetailsPage';
import { PaymentModulePage } from '../pages/paymentmodule/PaymentModulePage';
import { useProgramContext } from '../../programContext';
import { PeoplePaymentModulePage } from '@containers/pages/paymentmodulepeople/PeoplePaymentModulePage';
import { EditPeopleFollowUpPaymentPlanPage } from '@containers/pages/paymentmodulepeople/EditPeopleFollowUpPaymentPlanPage';
import { PeoplePaymentDetailsPage } from '@containers/pages/paymentmodulepeople/PeoplePaymentDetailsPage';
import { PeoplePaymentPlanDetailsPage } from '@containers/pages/paymentmodulepeople/PeoplePaymentPlanDetailsPage';
import { PeopleFollowUpPaymentPlanDetailsPage } from '@containers/pages/paymentmodulepeople/PeopleFollowUpPaymentPlanDetailsPage';
import { ProgramCyclePage } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCyclePage';
import { ProgramCycleDetailsPage } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsPage';
import { PaymentPlanDetailsPage } from '@containers/pages/paymentmodule/ProgramCycle/PaymentPlanDetails/PaymentPlanDetailsPage';
import { CreatePaymentPlanPage } from '@containers/pages/paymentmodule/ProgramCycle/CreatePaymentPlanPage';
import { EditPeoplePaymentPlanPage } from '@containers/pages/paymentmodulepeople/EditPeoplePaymentPlanPage';
import { ReactElement } from 'react';

export const PaymentModuleRoutes = (): ReactElement => {
  const { isSocialDctType } = useProgramContext();
  let children = [];

  if (isSocialDctType) {
    children = [
      {
        path: 'payment-plans',
        children: [
          {
            path: '',
            element: <PeoplePaymentModulePage />,
          },
          {
            path: ':paymentPlanId',
            children: [
              {
                path: '',
                element: <PeoplePaymentPlanDetailsPage />,
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
            element: <PeopleFollowUpPaymentPlanDetailsPage />,
          },
          {
            path: 'edit',
            element: <EditPeopleFollowUpPaymentPlanPage />,
          },
        ],
      },
      {
        path: 'payments/:paymentId',
        element: <PeoplePaymentDetailsPage />,
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
                        element: <PeoplePaymentPlanDetailsPage />,
                      },
                      {
                        path: 'edit',
                        element: <EditPeoplePaymentPlanPage />,
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
  } else {
    children = [
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
  }

  return useRoutes([
    {
      path: 'payment-module',
      children,
    },
  ]);
};
