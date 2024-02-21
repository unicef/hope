import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { ReportingDetailsPage } from '../pages/reporting/ReportingDetailsPage';
import { ReportingPage } from '../pages/reporting/ReportingPage';
import { GrievanceRoutes } from './GrievanceRoutes';
import { ProgramRoutes } from './ProgramRoutes';

export const AllProgramsRoutesSwitch = (): React.ReactElement => {
  const allProgramsRoutes = [
    {
      path: 'country-dashboard',
      element: <DashboardPage />,
    },
    {
      path: 'reporting/:id',
      element: <ReportingDetailsPage />,
    },
    {
      path: 'reporting',
      element: <ReportingPage />,
    },
    {
      path: 'activity-log',
      element: <ActivityLogPage />,
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
