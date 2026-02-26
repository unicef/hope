import { useRoutes, Navigate } from 'react-router-dom';
import { ReactElement } from 'react';
import CreateTargetPopulationPage from '@containers/pages/targeting/CreateTargetPopulationPage';
import EditTargetPopulationPage from '@containers/pages/targeting/EditTargetPopulationPage';
import TargetPopulationDetailsPage from '@containers/pages/targeting/TargetPopulationDetailsPage';
import TargetPopulationsPage from '@containers/pages/targeting/TargetPopulationsPage';

export const TargetingRoutes = (): ReactElement => {
  const targetingRoutes = [
    {
      path: 'target-population',
      children: [
        {
          path: '',
          element: <TargetPopulationsPage />,
        },
        {
          path: 'create',
          element: <CreateTargetPopulationPage />,
        },
        {
          path: 'edit-tp/:id',
          element: <EditTargetPopulationPage />,
        },
        {
          path: ':id',
          element: <TargetPopulationDetailsPage />,
        },
        {
          path: '*',
          element: <Navigate to="/404" replace />,
        },
      ],
    },
  ];

  return useRoutes(targetingRoutes);
};
