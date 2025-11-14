import { useRoutes } from 'react-router-dom';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { GrievanceRoutes } from './GrievanceRoutes';
import { PaymentModuleRoutes } from './PaymentModuleRoutes';
import { PaymentVerificationRoutes } from './PaymentVerificationRoutes';
import { PopulationRoutes } from './PopulationRoutes';
import { ProgramRoutes } from './ProgramRoutes';
import { RegistrationRoutes } from './RegistrationRoutes';
import { TargetingRoutes } from './TargetingRoutes';
import { AccountabilityRoutes } from './AccountabilityRoutes';
import { ReactElement } from 'react';
import { NewDashboardPage } from '@containers/pages/dashboard/NewDashboardPage';
import UsersPage from '@containers/pages/core/UsersPage';

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
