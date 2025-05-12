import { useRoutes } from 'react-router-dom';
import { ReactElement } from 'react';
import CreateSurveyPage from '@containers/pages/accountability/surveys/CreateSurveyPage';
import SurveyDetailsPage from '@containers/pages/accountability/surveys/SurveyDetailsPage';
import SurveysPage from '@containers/pages/accountability/surveys/SurveysPage';
import CreateCommunicationPage from '@containers/pages/accountability/communication/CreateCommunicationPage';
import CommunicationDetailsPage from '@containers/pages/accountability/communication/CommunicationDetailsPage';
import CommunicationPage from '@containers/pages/accountability/communication/CommunicationPage';

export const AccountabilityRoutes = (): ReactElement => {
  const accountabilityRoutes = [
    {
      path: 'accountability/surveys/create/*',
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
