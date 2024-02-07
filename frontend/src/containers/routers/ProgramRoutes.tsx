import * as React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '@components/core/SentryRoute';
import { ProgramDetailsPage } from '../pages/program/ProgramDetailsPage';
import { ProgramsPage } from '../pages/program/ProgramsPage';
import { CreateProgramPage } from '../pages/program/CreateProgramPage';
import { EditProgramPage } from '../pages/program/EditProgramPage';
import { DuplicateProgramPage } from '../pages/program/DuplicateProgramPage';

export function ProgramRoutes(): React.ReactElement {
  const { path } = useRouteMatch();

  const programRoutes = [
    {
      path: `${path}/list`,
      component: <ProgramsPage />,
    },
    {
      path: `${path}/create`,
      component: <CreateProgramPage />,
    },
    {
      path: `${path}/edit/:id`,
      component: <EditProgramPage />,
    },
    {
      path: `${path}/duplicate/:id`,
      component: <DuplicateProgramPage />,
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
}
