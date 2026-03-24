import { useRoutes, Navigate, useParams } from 'react-router-dom';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { ReactElement, Suspense } from 'react';
import { NewDashboardPage } from '@containers/pages/dashboard/NewDashboardPage';
import UsersPage from '@containers/pages/core/UsersPage';
import { LoadingComponent } from '@components/core/LoadingComponent';
import {
  LazyAccountabilityRoutes,
  LazyGrievanceRoutes,
  LazyPaymentModuleRoutes,
  LazyPaymentVerificationRoutes,
  LazyPopulationRoutes,
  LazyProgramRoutes,
  LazyRegistrationRoutes,
  LazyTargetingRoutes,
} from './lazyRoutes';

const SELECTED_PROGRAM_KNOWN_PREFIXES = new Set([
  // Direct routes
  'country-dashboard',
  'users-list',
  'activity-log',
  // Lazy route prefixes
  'accountability',
  'registration-data-import',
  'population',
  'target-population',
  'payment-module',
  'payment-verification',
  'grievance',
  // ProgramRoutes (no prefix)
  'list',
  'create',
  'edit',
  'duplicate',
  'details',
]);

export const SelectedProgramRoutesSwitch = (): ReactElement => {
  const { '*': splat = '' } = useParams();
  const firstSegment = splat.split('/')[0];
  const isUnknownPrefix =
    !!firstSegment && !SELECTED_PROGRAM_KNOWN_PREFIXES.has(firstSegment);

  const routes = useRoutes([
    {
      path: 'country-dashboard',
      element: <NewDashboardPage />,
    },
    {
      path: 'users-list',
      element: <UsersPage />,
    },
    {
      path: 'activity-log',
      element: <ActivityLogPage />,
    },
  ]);

  if (isUnknownPrefix) {
    return <Navigate to="/404" replace />;
  }

  return (
    <Suspense fallback={<LoadingComponent />}>
      {routes}
      <LazyAccountabilityRoutes />
      <LazyRegistrationRoutes />
      <LazyPopulationRoutes />
      <LazyProgramRoutes />
      <LazyTargetingRoutes />
      <LazyPaymentModuleRoutes />
      <LazyPaymentVerificationRoutes />
      <LazyGrievanceRoutes />
    </Suspense>
  );
};
