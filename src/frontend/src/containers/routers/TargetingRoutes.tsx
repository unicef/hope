import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { CreateTargetPopulationPage } from '../pages/targeting/CreateTargetPopulationPage';
import { EditTargetPopulationPage } from '../pages/targeting/EditTargetPopulationPage';
import { TargetPopulationDetailsPage } from '../pages/targeting/TargetPopulationDetailsPage';
import { TargetPopulationsPage } from '../pages/targeting/TargetPopulationsPage';

export const TargetingRoutes = (): React.ReactElement => {
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
