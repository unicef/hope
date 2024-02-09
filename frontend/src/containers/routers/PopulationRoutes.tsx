import * as React from 'react';
import { useRoutes, useLocation } from 'react-router-dom';
import { SentryRoute } from '@components/core/SentryRoute';
import { PopulationHouseholdDetailsPage } from '../pages/population/PopulationHouseholdDetailsPage';
import { PopulationHouseholdPage } from '../pages/population/PopulationHouseholdPage';
import { PopulationIndividualsDetailsPage } from '../pages/population/PopulationIndividualsDetailsPage';
import { PopulationIndividualsPage } from '../pages/population/PopulationIndividualsPage';

export const PopulationRoutes = (): React.ReactElement => {
  const location = useLocation();
  const path = location.pathname;

  const populationRoutes = [
    {
      path: `${path}/population/household/:id`,
      element: (
        <SentryRoute
          path={`${path}/population/household/:id`}
          element={<PopulationHouseholdDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/population/individuals/:id`,
      element: (
        <SentryRoute
          path={`${path}/population/individuals/:id`}
          element={<PopulationIndividualsDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/population/household`,
      element: (
        <SentryRoute
          path={`${path}/population/household`}
          element={<PopulationHouseholdPage />}
        />
      ),
    },
    {
      path: `${path}/population/individuals`,
      element: (
        <SentryRoute
          path={`${path}/population/individuals`}
          element={<PopulationIndividualsPage />}
        />
      ),
    },
  ];

  const routes = useRoutes(populationRoutes);

  return routes;
};
