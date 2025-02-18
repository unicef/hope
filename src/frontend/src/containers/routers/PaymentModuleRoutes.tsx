import { useRoutes } from 'react-router-dom';
import EditFollowUpPaymentPlanPage from '@containers/pages/paymentmodule/EditFollowUpPaymentPlanPage';
import EditFollowUpSetUpFspPage from '@containers/pages/paymentmodule/EditFollowUpSetUpFspPage';
import EditPaymentPlanPage from '@containers/pages/paymentmodule/EditPaymentPlanPage';
import EditSetUpFspPage from '@containers/pages/paymentmodule/EditSetUpFspPage';
import FollowUpPaymentPlanDetailsPage from '@containers/pages/paymentmodule/FollowUpPaymentPlanDetailsPage';
import PaymentDetailsPage from '@containers/pages/paymentmodule/PaymentDetailsPage';
import PaymentModulePage from '@containers/pages/paymentmodule/PaymentModulePage';
import CreatePaymentPlanPage from '@containers/pages/paymentmodule/ProgramCycle/CreatePaymentPlanPage';
import PaymentPlanDetailsPage from '@containers/pages/paymentmodule/ProgramCycle/PaymentPlanDetails/PaymentPlanDetailsPage';
import ProgramCycleDetailsPage from '@containers/pages/paymentmodule/ProgramCycle/ProgramCycleDetails/ProgramCycleDetailsPage';
import ProgramCyclePage from '@containers/pages/paymentmodule/ProgramCycle/ProgramCyclePage';
import SetUpFollowUpFspPage from '@containers/pages/paymentmodule/SetUpFollowUpFspPage';
import { SetUpFspPage } from '@containers/pages/paymentmodule/SetUpFspPage';
import EditPeopleFollowUpPaymentPlanPage from '@containers/pages/paymentmodulepeople/EditPeopleFollowUpPaymentPlanPage';
import { EditPeopleFollowUpSetUpFspPage } from '@containers/pages/paymentmodulepeople/EditPeopleFollowUpSetUpFspPage';
import EditPeoplePaymentPlanPage from '@containers/pages/paymentmodulepeople/EditPeoplePaymentPlanPage';
import PeopleFollowUpPaymentPlanDetailsPage from '@containers/pages/paymentmodulepeople/PeopleFollowUpPaymentPlanDetailsPage';
import PeoplePaymentDetailsPage from '@containers/pages/paymentmodulepeople/PeoplePaymentDetailsPage';
import PeoplePaymentModulePage from '@containers/pages/paymentmodulepeople/PeoplePaymentModulePage';
import PeoplePaymentPlanDetailsPage from '@containers/pages/paymentmodulepeople/PeoplePaymentPlanDetailsPage';
import { SetUpPeopleFollowUpFspPage } from '@containers/pages/paymentmodulepeople/SetUpPeopleFollowUpFspPage';
import { useProgramContext } from 'src/programContext';
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
              {
                path: 'setup-fsp/edit',
                element: <EditSetUpFspPage />,
              },
              {
                path: 'setup-fsp/create',
                element: <SetUpFspPage />,
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
          {
            path: 'setup-fsp/edit',
            element: <EditPeopleFollowUpSetUpFspPage />,
          },
          {
            path: 'setup-fsp/create',
            element: <SetUpPeopleFollowUpFspPage />,
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
              {
                path: 'setup-fsp/edit',
                element: <EditSetUpFspPage />,
              },
              {
                path: 'setup-fsp/create',
                element: <SetUpFspPage />,
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
          {
            path: 'setup-fsp/edit',
            element: <EditFollowUpSetUpFspPage />,
          },
          {
            path: 'setup-fsp/create',
            element: <SetUpFollowUpFspPage />,
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
