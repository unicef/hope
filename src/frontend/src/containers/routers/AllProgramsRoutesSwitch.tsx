import { useRoutes } from 'react-router-dom';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import ReportingDetailsPage from '../pages/reporting/ReportingDetailsPage';
import ReportingPage from '../pages/reporting/ReportingPage';
import { GrievanceRoutes } from './GrievanceRoutes';
import { ProgramRoutes } from './ProgramRoutes';
import { ManagerialConsolePage } from '@containers/pages/managerialConsole/ManagerialConsolePage';
import { ReactElement } from 'react';
import { NewDashboardPage } from '@containers/pages/dashboard/NewDashboardPage';

export const AllProgramsRoutesSwitch = (): ReactElement => {
  const allProgramsRoutes = [
    {
      path: 'country-dashboard',
      element: <NewDashboardPage />,
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
    { path: 'managerial-console', element: <ManagerialConsolePage /> },
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
