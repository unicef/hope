import React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { ReportingDetailsPage } from '../pages/reporting/ReportingDetailsPage';
import { ReportingPage } from '../pages/reporting/ReportingPage';
import { GrievanceRoutes } from './GrievanceRoutes';
import { ProgramRoutes } from './ProgramRoutes';

export function AllProgramsRoutesSwitch(): React.ReactElement {
  const { path } = useRouteMatch();
  return (
    <>
      <Switch>
        <SentryRoute label="/ - Dashboard" path={`${path}/country-dashboard`}>
          <DashboardPage />
        </SentryRoute>
        <SentryRoute path={`${path}/reporting/:id`}>
          <ReportingDetailsPage />
        </SentryRoute>
        <SentryRoute path={`${path}/reporting`}>
          <ReportingPage />
        </SentryRoute>
        <SentryRoute path={`${path}/activity-log`}>
          <ActivityLogPage />
        </SentryRoute>
      </Switch>
      <GrievanceRoutes />
      <ProgramRoutes />
    </>
  );
}
