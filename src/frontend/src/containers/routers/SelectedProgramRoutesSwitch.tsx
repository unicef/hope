import { useRoutes } from 'react-router-dom';
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

export const SelectedProgramRoutesSwitch = (): ReactElement => {
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
