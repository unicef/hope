import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { CommunicationDetailsPage } from '../pages/accountability/communication/CommunicationDetailsPage';
import { CommunicationPage } from '../pages/accountability/communication/CommunicationPage';
import { CreateCommunicationPage } from '../pages/accountability/communication/CreateCommunicationPage';
import { CreateSurveyPage } from '../pages/accountability/surveys/CreateSurveyPage';
import { SurveyDetailsPage } from '../pages/accountability/surveys/SurveyDetailsPage';
import { SurveysPage } from '../pages/accountability/surveys/SurveysPage';

export const AccountabilityRoutes = (): React.ReactElement => {
  const accountabilityRoutes = [
    {
      path: 'accountability/surveys/create',
      element: <CreateSurveyPage />,
    },
    {
      path: 'accountability/surveys/:id',
      element: <SurveyDetailsPage />,
    },
    {
      path: 'accountability/surveys',
      element: <SurveysPage />,
    },
    {
      path: 'accountability/communication/create',
      element: <CreateCommunicationPage />,
    },
    {
      path: 'accountability/communication/:id',
      element: <CommunicationDetailsPage />,
    },
    {
      path: 'accountability/communication',
      element: <CommunicationPage />,
    },
  ];

  return useRoutes(accountabilityRoutes);
};
