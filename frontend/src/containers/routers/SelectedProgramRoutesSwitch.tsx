import * as React from 'react';
import { Route, useRoutes } from 'react-router-dom';
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

export const SelectedProgramRoutesSwitch = (): React.ReactElement => {
  const routes = useRoutes([
    {
      path: 'country-dashboard',
      element: (
        <Route
          // label="/ - Dashboard"
          path="country-dashboard"
          element={<DashboardPage />}
        />
      ),
    },
    {
      path: 'payment-records/:id',
      element: (
        <Route
          path="payment-records/:id"
          element={<PaymentRecordDetailsPage />}
        />
      ),
    },
    {
      path: 'reporting/:id',
      element: (
        <Route path="reporting/:id" element={<ReportingDetailsPage />} />
      ),
    },
    {
      path: 'reporting',
      element: <Route path="reporting" element={<ReportingPage />} />,
    },
    {
      path: 'users-list',
      element: <Route path="users-list" element={<UsersPage />} />,
    },
    {
      path: 'activity-log',
      element: (
        <Route path="activity-log" element={<ActivityLogPage />} />
      ),
    },
  ]);

  return (
    <>
      {routes}
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
};
