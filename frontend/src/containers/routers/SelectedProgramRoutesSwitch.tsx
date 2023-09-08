import React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { UsersPage } from '../pages/core/UsersPage';
import { PaymentRecordDetailsPage } from '../pages/payments/PaymentRecordDetailsPage';
import { ReportingDetailsPage } from '../pages/reporting/ReportingDetailsPage';
import { ReportingPage } from '../pages/reporting/ReportingPage';
import { RegistrationRoutes } from './RegistrationRoutes';
import { ProgramRoutes } from './ProgramRoutes';
import { TargetingRoutes } from './TargetingRoutes';
import { PaymentModuleRoutes } from './PaymentModuleRoutes';
import { PaymentVerificationRoutes } from './PaymentVerificationRoutes';
import { GrievanceRoutes } from './GrievanceRoutes';
import { PopulationRoutes } from './PopulationRoutes';
import { AccountabilityRoutes } from './AccountabilityRoutes';

export const SelectedProgramRoutesSwitch = (): React.ReactElement => {
  const { path } = useRouteMatch();
  return (
    <>
      <Switch>
        <SentryRoute path={`${path}/payment-records/:id`}>
          <PaymentRecordDetailsPage />
        </SentryRoute>
        <SentryRoute path={`${path}/reporting/:id`}>
          <ReportingDetailsPage />
        </SentryRoute>
        <SentryRoute path={`${path}/reporting`}>
          <ReportingPage />
        </SentryRoute>
        <SentryRoute path={`${path}/users-list`}>
          <UsersPage />
        </SentryRoute>
        <SentryRoute path={`${path}/activity-log`}>
          <ActivityLogPage />
        </SentryRoute>
      </Switch>
      <RegistrationRoutes />
      <PopulationRoutes />
      <ProgramRoutes />
      <TargetingRoutes />
      <PaymentModuleRoutes />
      <PaymentVerificationRoutes />
      <GrievanceRoutes />
      <AccountabilityRoutes />
    </>
  );
};
