import { useRoutes } from 'react-router-dom';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { GrievanceRoutes } from './GrievanceRoutes';
import { ProgramRoutes } from './ProgramRoutes';
import { ManagerialConsolePage } from '@containers/pages/managerialConsole/ManagerialConsolePage';
import { ReactElement } from 'react';
import { NewDashboardPage } from '@containers/pages/dashboard/NewDashboardPage';
import CountrySearchPage from '@containers/pages/countrySearch/CountrySearchPage';

export const AllProgramsRoutesSwitch = (): ReactElement => {
  const allProgramsRoutes = [
    {
      path: 'country-dashboard',
      element: <NewDashboardPage />,
    },
    {
      path: 'activity-log',
      element: <ActivityLogPage />,
    },
    { path: 'managerial-console', element: <ManagerialConsolePage /> },
    {
      path: 'country-search',
      element: <CountrySearchPage />,
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
