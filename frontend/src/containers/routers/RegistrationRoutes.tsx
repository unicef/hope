import React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { RegistrationDataImportDetailsPage } from '../pages/rdi/RegistrationDataImportDetailsPage';
import { RegistrationDataImportPage } from '../pages/rdi/RegistrationDataImportPage';
import { RegistrationHouseholdDetailsPage } from '../pages/rdi/RegistrationHouseholdDetailsPage';
import { RegistrationIndividualDetailsPage } from '../pages/rdi/RegistrationIndividualDetailsPage';

export function RegistrationRoutes(): React.ReactElement {
  const { path } = useRouteMatch();

  const registrationRoutes = [
    {
      path: `${path}/registration-data-import/household/:id`,
      component: <RegistrationHouseholdDetailsPage />,
    },
    {
      path: `${path}/registration-data-import/individual/:id`,
      component: <RegistrationIndividualDetailsPage />,
    },
    {
      path: `${path}/registration-data-import/:id`,
      component: <RegistrationDataImportDetailsPage />,
    },
    {
      path: `${path}/registration-data-import`,
      component: <RegistrationDataImportPage />,
    },
  ];

  return (
    <Switch>
      {registrationRoutes.map((route) => (
        <SentryRoute key={route.path} path={route.path}>
          {route.component}
        </SentryRoute>
      ))}
    </Switch>
  );
}
