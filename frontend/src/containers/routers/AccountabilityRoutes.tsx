import React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { CommunicationDetailsPage } from '../pages/accountability/communication/CommunicationDetailsPage';
import { CommunicationPage } from '../pages/accountability/communication/CommunicationPage';
import { CreateCommunicationPage } from '../pages/accountability/communication/CreateCommunicationPage';
import { CreateSurveyPage } from '../pages/accountability/surveys/CreateSurveyPage';
import { SurveyDetailsPage } from '../pages/accountability/surveys/SurveyDetailsPage';
import { SurveysPage } from '../pages/accountability/surveys/SurveysPage';

export const AccountabilityRoutes = (): React.ReactElement => {
  const { path } = useRouteMatch();

  const accountabilityRoutes = [
    {
      path: `${path}/accountability/surveys/create`,
      component: <CreateSurveyPage />,
    },
    {
      path: `${path}/accountability/surveys/:id`,
      component: <SurveyDetailsPage />,
    },
    {
      path: `${path}/accountability/surveys`,
      component: <SurveysPage />,
      exact: true,
    },
    {
      path: `${path}/accountability/communication/create`,
      component: <CreateCommunicationPage />,
    },
    {
      path: `${path}/accountability/communication/:id`,
      component: <CommunicationDetailsPage />,
    },
    {
      path: `${path}/accountability/communication`,
      component: <CommunicationPage />,
      exact: true,
    },
  ];

  return (
    <Switch>
      {accountabilityRoutes.map((route) => (
        <SentryRoute key={route.path} path={route.path} exact={route.exact}>
          {route.component}
        </SentryRoute>
      ))}
    </Switch>
  );
};
