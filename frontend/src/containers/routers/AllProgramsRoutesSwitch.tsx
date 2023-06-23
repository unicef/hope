import React from 'react';
import { Redirect, Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { ProgramsPage } from '../pages/program/ProgramsPage';
import { ProgramDetailsPage } from '../pages/program/ProgramDetailsPage';

export const AllProgramsRoutesSwitch = (): React.ReactElement => {
  const { path } = useRouteMatch();
  return (
    <Switch>
      <SentryRoute path={`${path}/list`}>
        <ProgramsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/details/:id`}>
        <ProgramDetailsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/`}>
        <Redirect to='/' />
      </SentryRoute>
    </Switch>
  );
};
