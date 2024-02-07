import * as React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '@components/core/SentryRoute';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { UsersPage } from '../pages/core/UsersPage';
import { PaymentRecordDetailsPage } from '../pages/payments/PaymentRecordDetailsPage';
import { ReportingDetailsPage } from '../pages/reporting/ReportingDetailsPage';
import { ReportingPage } from '../pages/reporting/ReportingPage';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { GrievanceRoutes } from './GrievanceRoutes';
import { PaymentModuleRoutes } from './PaymentModuleRoutes';
import { PaymentVerificationRoutes } from './PaymentVerificationRoutes';
import { PopulationRoutes } from './PopulationRoutes';
import { ProgramRoutes } from './ProgramRoutes';
import { RegistrationRoutes } from './RegistrationRoutes';
import { TargetingRoutes } from './TargetingRoutes';
import { AccountabilityRoutes } from './AccountabilityRoutes';

export function SelectedProgramRoutesSwitch(): React.ReactElement {
  const { path } = useRouteMatch();
  return (
    <>
      <Switch>
        <SentryRoute label="/ - Dashboard" path={`${path}/country-dashboard`}>
          <DashboardPage />
        </SentryRoute>
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
      <AccountabilityRoutes />
      <RegistrationRoutes />
      <PopulationRoutes />
      <ProgramRoutes />
      <TargetingRoutes />
      <PaymentModuleRoutes />
      <PaymentVerificationRoutes />
      <GrievanceRoutes />
    </>
  );
}
