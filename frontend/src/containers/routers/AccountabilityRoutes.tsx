import React from 'react';
import { useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { CommunicationDetailsPage } from '../pages/accountability/communication/CommunicationDetailsPage';
import { CommunicationPage } from '../pages/accountability/communication/CommunicationPage';
import { CreateCommunicationPage } from '../pages/accountability/communication/CreateCommunicationPage';
import { CreateSurveyPage } from '../pages/accountability/surveys/CreateSurveyPage';
import { SurveyDetailsPage } from '../pages/accountability/surveys/SurveyDetailsPage';
import { SurveysPage } from '../pages/accountability/surveys/SurveysPage';

export const AccountabilityRoutes = (): React.ReactElement => {
  const { path } = useRouteMatch();
  return (
    <>
      <SentryRoute path={`${path}/accountability/surveys/create`}>
        <CreateSurveyPage />
      </SentryRoute>
      <SentryRoute path={`${path}/accountability/surveys/:id`}>
        <SurveyDetailsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/accountability/surveys`}>
        <SurveysPage />
      </SentryRoute>
      <SentryRoute path={`${path}/accountability/communication/create`}>
        <CreateCommunicationPage />
      </SentryRoute>
      <SentryRoute path={`${path}/accountability/communication/:id`}>
        <CommunicationDetailsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/accountability/communication`}>
        <CommunicationPage />
      </SentryRoute>
    </>
  );
};
