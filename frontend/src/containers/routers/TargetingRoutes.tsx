import * as React from 'react';
import { Route, useLocation, useRoutes } from 'react-router-dom';
import { CreateTargetPopulationPage } from '../pages/targeting/CreateTargetPopulationPage';
import { EditTargetPopulationPage } from '../pages/targeting/EditTargetPopulationPage';
import { TargetPopulationDetailsPage } from '../pages/targeting/TargetPopulationDetailsPage';
import { TargetPopulationsPage } from '../pages/targeting/TargetPopulationsPage';

export const TargetingRoutes = (): React.ReactElement => {
  const location = useLocation();
  const path = location.pathname;

  const targetingRoutes = [
    {
      path: `${path}/target-population`,
      element: (
        <Route
          path={`${path}/target-population`}
          element={<TargetPopulationsPage />}
        />
      ),
    },
    {
      path: `${path}/target-population/create`,
      element: (
        <Route
          path={`${path}/target-population/create`}
          element={<CreateTargetPopulationPage />}
        />
      ),
    },
    {
      path: `${path}/target-population/edit-tp/:id`,
      element: (
        <Route
          path={`${path}/target-population/edit-tp/:id`}
          element={<EditTargetPopulationPage />}
        />
      ),
    },
    {
      path: `${path}/target-population/:id`,
      element: (
        <Route
          path={`${path}/target-population/:id`}
          element={<TargetPopulationDetailsPage />}
        />
      ),
    },
  ];

  return useRoutes(targetingRoutes);
};
