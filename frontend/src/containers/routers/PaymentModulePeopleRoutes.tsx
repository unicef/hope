import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { CreatePeoplePaymentPlanPage } from '../pages/paymentmodulepeople/CreatePeoplePaymentPlanPage';
import { EditPeopleFollowUpPaymentPlanPage } from '../pages/paymentmodulepeople/EditPeopleFollowUpPaymentPlanPage';
import { EditPeopleFollowUpSetUpFspPage } from '../pages/paymentmodulepeople/EditPeopleFollowUpSetUpFspPage';
import { EditPeoplePaymentPlanPage } from '../pages/paymentmodulepeople/EditPeoplePaymentPlanPage';
import { EditPeopleSetUpFspPage } from '../pages/paymentmodulepeople/EditPeopleSetUpFspPage';
import { PeopleFollowUpPaymentPlanDetailsPage } from '../pages/paymentmodulepeople/PeopleFollowUpPaymentPlanDetailsPage';
import { PeoplePaymentDetailsPage } from '../pages/paymentmodulepeople/PeoplePaymentDetailsPage';
import { PeoplePaymentModulePage } from '../pages/paymentmodulepeople/PeoplePaymentModulePage';
import { PeoplePaymentPlanDetailsPage } from '../pages/paymentmodulepeople/PeoplePaymentPlanDetailsPage';
import { SetUpPeopleFspPage } from '../pages/paymentmodulepeople/SetUpPeopleFspPage';
import { SetUpPeopleFollowUpFspPage } from '../pages/paymentmodulepeople/SetUpPeopleFollowUpFspPage';

export const PaymentModulePeopleRoutes = (): React.ReactElement => {
  const paymentModulePeopleRoutes = [
    {
      path: 'payment-module-people/new-plan',
      element: <CreatePeoplePaymentPlanPage />,
    },
    {
      path: 'payment-module-people',
      element: <PeoplePaymentModulePage />,
    },
    {
      path: 'payment-module-people/followup-payment-plans/:id/edit',
      element: <EditPeopleFollowUpPaymentPlanPage />,
    },
    {
      path: 'payment-module-people/followup-payment-plans/:id/setup-fsp/edit',
      element: <EditPeopleFollowUpSetUpFspPage />,
    },
    {
      path: 'payment-module-people/followup-payment-plans/:id/setup-fsp/create',
      element: <SetUpPeopleFollowUpFspPage />,
    },
    {
      path: 'payment-module-people/payment-plans/:id/setup-fsp/edit',
      element: <EditPeopleSetUpFspPage />,
    },
    {
      path: 'payment-module-people/payment-plans/:id/edit',
      element: <EditPeoplePaymentPlanPage />,
    },
    {
      path: 'payment-module-people/payments/:id',
      element: <PeoplePaymentDetailsPage />,
    },
    {
      path: 'payment-module-people/payment-plans/:id/setup-fsp/create',
      element: <SetUpPeopleFspPage />,
    },
    {
      path: 'payment-module-people/payment-plans/:id',
      element: <PeoplePaymentPlanDetailsPage />,
    },
    {
      path: 'payment-module-people/followup-payment-plans/:id',
      element: <PeopleFollowUpPaymentPlanDetailsPage />,
    },
  ];

  return useRoutes(paymentModulePeopleRoutes);
};
