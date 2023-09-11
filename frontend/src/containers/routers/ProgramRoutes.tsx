import React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { ProgramCycleDetailsPageProgramDetails } from '../pages/program/ProgramCycleDetailsPageProgramDetails';
import { ProgramDetailsPage } from '../pages/program/ProgramDetailsPage';
import { ProgramsPage } from '../pages/program/ProgramsPage';

export const ProgramRoutes = (): React.ReactElement => {
  const { path } = useRouteMatch();

  const programRoutes = [
    {
      path: `${path}/list`,
      component: <ProgramsPage />,
    },
    {
      path: `${path}/details/:id/program-cycles/:programCycleId`,
      component: <ProgramCycleDetailsPageProgramDetails />,
    },
    {
      path: `${path}/details/:id`,
      component: <ProgramDetailsPage />,
    },
  ];

  return (
    <Switch>
      {programRoutes.map((route) => (
        <SentryRoute key={route.path} path={route.path}>
          {route.component}
        </SentryRoute>
      ))}
    </Switch>
  );
};
