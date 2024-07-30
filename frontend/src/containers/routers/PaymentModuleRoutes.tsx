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
import { useProgramContext } from '../../programContext';
import { CreatePeoplePaymentPlanPage } from '@containers/pages/paymentmodulepeople/CreatePeoplePaymentPlanPage';
import { PeoplePaymentModulePage } from '@containers/pages/paymentmodulepeople/PeoplePaymentModulePage';
import { EditPeopleFollowUpPaymentPlanPage } from '@containers/pages/paymentmodulepeople/EditPeopleFollowUpPaymentPlanPage';
import { EditPeopleFollowUpSetUpFspPage } from '@containers/pages/paymentmodulepeople/EditPeopleFollowUpSetUpFspPage';
import { SetUpPeopleFollowUpFspPage } from '@containers/pages/paymentmodulepeople/SetUpPeopleFollowUpFspPage';
import { EditPeopleSetUpFspPage } from '@containers/pages/paymentmodulepeople/EditPeopleSetUpFspPage';
import { EditPeoplePaymentPlanPage } from '@containers/pages/paymentmodulepeople/EditPeoplePaymentPlanPage';
import { PeoplePaymentDetailsPage } from '@containers/pages/paymentmodulepeople/PeoplePaymentDetailsPage';
import { SetUpPeopleFspPage } from '@containers/pages/paymentmodulepeople/SetUpPeopleFspPage';
import { PeoplePaymentPlanDetailsPage } from '@containers/pages/paymentmodulepeople/PeoplePaymentPlanDetailsPage';
import { PeopleFollowUpPaymentPlanDetailsPage } from '@containers/pages/paymentmodulepeople/PeopleFollowUpPaymentPlanDetailsPage';
import { ProgramCyclePage } from '@containers/pages/paymentmodule/ProgramCycle/ProgramCyclePage';

export const PaymentModuleRoutes = (): React.ReactElement => {
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
            path: 'new-plan',
            element: <CreatePeoplePaymentPlanPage />,
          },
          {
            path: ':id',
            children: [
              {
                path: '',
                element: <PeoplePaymentPlanDetailsPage />,
              },
              {
                path: 'edit',
                element: <EditPeoplePaymentPlanPage />,
              },
              {
                path: 'setup-fsp/edit',
                element: <EditPeopleSetUpFspPage />,
              },
              {
                path: 'setup-fsp/create',
                element: <SetUpPeopleFspPage />,
              },
            ],
          },
        ],
      },
      {
        path: 'followup-payment-plans/:id',
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
        path: 'payments/:id',
        element: <PeoplePaymentDetailsPage />,
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
            path: 'new-plan',
            element: <CreatePaymentPlanPage />,
          },
          {
            path: ':id',
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
        path: 'followup-payment-plans/:id',
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
        path: 'payments/:id',
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
            path: ':id',
            element: false,
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
