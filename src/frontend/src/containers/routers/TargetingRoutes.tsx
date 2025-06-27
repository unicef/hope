import { useRoutes } from 'react-router-dom';
import { ReactElement } from 'react';
import CreateTargetPopulationPage from '@containers/pages/targeting/CreateTargetPopulationPage';
import EditTargetPopulationPage from '@containers/pages/targeting/EditTargetPopulationPage';
import TargetPopulationDetailsPage from '@containers/pages/targeting/TargetPopulationDetailsPage';
import TargetPopulationsPage from '@containers/pages/targeting/TargetPopulationsPage';

export const TargetingRoutes = (): ReactElement => {
  const targetingRoutes = [
    {
      path: 'target-population',
      element: <TargetPopulationsPage />,
    },
    {
      path: 'target-population/create',
      element: <CreateTargetPopulationPage />,
    },
    {
      path: 'target-population/edit-tp/:id',
      element: <EditTargetPopulationPage />,
    },
    {
      path: 'target-population/:id',
      element: <TargetPopulationDetailsPage />,
    },
  ];

  return useRoutes(targetingRoutes);
};
