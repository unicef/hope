import React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { EditFollowUpPaymentPlanPage } from '../pages/paymentmodule/EditFollowUpPaymentPlanPage';
import { EditFollowUpSetUpFspPage } from '../pages/paymentmodule/EditFollowUpSetUpFspPage';
import { EditPaymentPlanPage } from '../pages/paymentmodule/EditPaymentPlanPage';
import { EditSetUpFspPage } from '../pages/paymentmodule/EditSetUpFspPage';
import { FollowUpPaymentPlanDetailsPage } from '../pages/paymentmodule/FollowUpPaymentPlanDetailsPage';
import { FollowUpPaymentPlansPage } from '../pages/paymentmodule/FollowUpPaymentPlansPage';
import { PaymentDetailsPage } from '../pages/paymentmodule/PaymentDetailsPage';
import { PaymentPlanDetailsPage } from '../pages/paymentmodule/PaymentPlanDetailsPage';
import { PaymentPlansPage } from '../pages/paymentmodule/PaymentPlansPage';
import { SetUpFspPage } from '../pages/paymentmodule/SetUpFspPage';
import { SetUpFspPageFollowUp } from '../pages/paymentmodule/SetUpFspPageFollowUp';
import { SetUpPaymentInstructionsPage } from '../pages/paymentmodule/SetUpPaymentInstructionsPage';
import { ProgramCycleDetailsPagePaymentModule } from '../pages/programcycles/ProgramCycleDetailsPagePaymentModule';
import { ProgramCyclesPagePaymentModule } from '../pages/programcycles/ProgramCyclesPagePaymentModule';
import { CreatePaymentPlanProgramCyclePage } from '../pages/programcycles/CreatePaymentPlanProgramCyclePage';

export const PaymentModuleRoutes = (): React.ReactElement => {
  const { path } = useRouteMatch();

  const paymentModuleRoutes = [
    {
      path: `${path}/payment-module/followup-payment-plans/:id/setup-fsp/edit`,
      component: <EditFollowUpSetUpFspPage />,
    },
    {
      path: `${path}/payment-module/followup-payment-plans/:id/setup-fsp/create`,
      component: <SetUpFspPageFollowUp />,
    },
    {
      path: `${path}/payment-module/followup-payment-plans/:id/edit`,
      component: <EditFollowUpPaymentPlanPage />,
    },
    {
      path: `${path}/payment-module/followup-payment-plans/:id`,
      component: <FollowUpPaymentPlanDetailsPage />,
    },
    {
      path: `${path}/payment-module/followup-payment-plans`,
      component: <FollowUpPaymentPlansPage />,
    },
    {
      path: `${path}/payment-module/payment-plans/:id/setup-fsp/edit`,
      component: <EditSetUpFspPage />,
    },
    {
      path: `${path}/payment-module/payment-plans/:id/setup-fsp/create`,
      component: <SetUpFspPage />,
    },
    {
      path: `${path}/payment-module/payment-plans/:id/setup-payment-instructions/create`,
      component: <SetUpPaymentInstructionsPage />,
    },
    {
      path: `${path}/payment-module/payment-plans/:id/edit`,
      component: <EditPaymentPlanPage />,
    },
    {
      path: `${path}/payment-module/payment-plans/:id`,
      component: <PaymentPlanDetailsPage />,
    },
    {
      path: `${path}/payment-module/payment-plans`,
      component: <PaymentPlansPage />,
    },
    {
      path: `${path}/payment-module/payments/:id`,
      component: <PaymentDetailsPage />,
    },
    {
      path: `${path}/payment-module/program-cycles/:id/create-payment-plan`,
      component: <CreatePaymentPlanProgramCyclePage />,
    },
    {
      path: `${path}/payment-module/program-cycles/:id`,
      component: <ProgramCycleDetailsPagePaymentModule />,
    },
    {
      path: `${path}/payment-module/program-cycles`,
      component: <ProgramCyclesPagePaymentModule />,
    },
  ];

  return (
    <Switch>
      {paymentModuleRoutes.map((route) => (
        <SentryRoute key={route.path} path={route.path}>
          {route.component}
        </SentryRoute>
      ))}
    </Switch>
  );
};
