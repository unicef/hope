import React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { PopulationHouseholdDetailsPage } from '../pages/population/PopulationHouseholdDetailsPage';
import { PopulationHouseholdPage } from '../pages/population/PopulationHouseholdPage';
import { PopulationIndividualsDetailsPage } from '../pages/population/PopulationIndividualsDetailsPage';
import { PopulationIndividualsPage } from '../pages/population/PopulationIndividualsPage';

export const PopulationRoutes = (): React.ReactElement => {
  const { path } = useRouteMatch();

  const populationRoutes = [
    {
      path: `${path}/population/household/:id`,
      component: <PopulationHouseholdDetailsPage />,
    },
    {
      path: `${path}/population/individuals/:id`,
      component: <PopulationIndividualsDetailsPage />,
    },
    {
      path: `${path}/population/household`,
      component: <PopulationHouseholdPage />,
    },
    {
      path: `${path}/population/individuals`,
      component: <PopulationIndividualsPage />,
    },
  ];

  return (
    <Switch>
      {populationRoutes.map((route) => (
        <SentryRoute key={route.path} path={route.path}>
          {route.component}
        </SentryRoute>
      ))}
    </Switch>
  );
};
