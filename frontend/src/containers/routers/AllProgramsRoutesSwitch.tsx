import * as React from 'react';
import { useRoutes, useLocation } from 'react-router-dom';
import { SentryRoute } from '@components/core/SentryRoute';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { ReportingDetailsPage } from '../pages/reporting/ReportingDetailsPage';
import { ReportingPage } from '../pages/reporting/ReportingPage';
import { GrievanceRoutes } from './GrievanceRoutes';
import { ProgramRoutes } from './ProgramRoutes';

export const AllProgramsRoutesSwitch = (): React.ReactElement => {
  const location = useLocation();
  const path = location.pathname;

  const allProgramsRoutes = [
    {
      path: `${path}/country-dashboard`,
      element: (
        <SentryRoute
          path={`${path}/country-dashboard`}
          element={<DashboardPage />}
        />
      ),
    },
    {
      path: `${path}/reporting/:id`,
      element: (
        <SentryRoute
          path={`${path}/reporting/:id`}
          element={<ReportingDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/reporting`,
      element: (
        <SentryRoute path={`${path}/reporting`} element={<ReportingPage />} />
      ),
    },
    {
      path: `${path}/activity-log`,
      element: (
        <SentryRoute
          path={`${path}/activity-log`}
          element={<ActivityLogPage />}
        />
      ),
    },
  ];

  const routes = useRoutes(allProgramsRoutes);

  return (
    <>
      {routes}
      <GrievanceRoutes />
      <ProgramRoutes />
    </>
  );
};
