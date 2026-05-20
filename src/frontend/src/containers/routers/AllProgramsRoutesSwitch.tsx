import { useRoutes, Navigate, useParams } from 'react-router-dom';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { ManagerialConsolePage } from '@containers/pages/managerialConsole/ManagerialConsolePage';
import { ReactElement, Suspense } from 'react';
import { NewDashboardPage } from '@containers/pages/dashboard/NewDashboardPage';
import CountrySearchPage from '@containers/pages/countrySearch/CountrySearchPage';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { LazyGrievanceRoutes, LazyProgramRoutes } from './lazyRoutes';

const ALL_PROGRAMS_KNOWN_PREFIXES = new Set([
  // Direct routes
  'country-dashboard',
  'activity-log',
  'managerial-console',
  'country-search',
  // Lazy route prefixes
  'grievance',
  // ProgramRoutes (no prefix)
  'list',
  'create',
  'edit',
  'duplicate',
  'details',
]);

export const AllProgramsRoutesSwitch = (): ReactElement => {
  const { '*': splat = '' } = useParams();
  const firstSegment = splat.split('/')[0];
  const isUnknownPrefix =
    !!firstSegment && !ALL_PROGRAMS_KNOWN_PREFIXES.has(firstSegment);

  const routes = useRoutes([
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
  ]);

  if (isUnknownPrefix) {
    return <Navigate to="/404" replace />;
  }

  return (
    <Suspense fallback={<LoadingComponent />}>
      {routes}
      <LazyGrievanceRoutes />
      <LazyProgramRoutes />
    </Suspense>
  );
};
