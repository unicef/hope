import * as React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '@components/core/SentryRoute';
import { CreateTargetPopulationPage } from '../pages/targeting/CreateTargetPopulationPage';
import { EditTargetPopulationPage } from '../pages/targeting/EditTargetPopulationPage';
import { TargetPopulationDetailsPage } from '../pages/targeting/TargetPopulationDetailsPage';
import { TargetPopulationsPage } from '../pages/targeting/TargetPopulationsPage';

export function TargetingRoutes(): React.ReactElement {
  const { path } = useRouteMatch();

  const targetingRoutes = [
    {
      path: `${path}/target-population`,
      component: <TargetPopulationsPage />,
      exact: true,
    },
    {
      path: `${path}/target-population/create`,
      component: <CreateTargetPopulationPage />,
    },
    {
      path: `${path}/target-population/edit-tp/:id`,
      component: <EditTargetPopulationPage />,
    },
    {
      path: `${path}/target-population/:id`,
      component: <TargetPopulationDetailsPage />,
    },
  ];

  return (
    <Switch>
      {targetingRoutes.map((route) => (
        <SentryRoute key={route.path} path={route.path} exact={route.exact}>
          {route.component}
        </SentryRoute>
      ))}
    </Switch>
  );
}
