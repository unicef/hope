import { useRoutes, Navigate } from 'react-router-dom';
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
      path: 'accountability',
      children: [
        {
          path: 'surveys/create/*',
          element: <CreateSurveyPage />,
        },
        {
          path: 'surveys/:id',
          element: <SurveyDetailsPage />,
        },
        {
          path: 'surveys',
          element: <SurveysPage />,
        },
        {
          path: 'communication/create',
          element: <CreateCommunicationPage />,
        },
        {
          path: 'communication/:id',
          element: <CommunicationDetailsPage />,
        },
        {
          path: 'communication',
          element: <CommunicationPage />,
        },
        {
          path: '*',
          element: <Navigate to="/404" replace />,
        },
      ],
    },
  ];

  return useRoutes(accountabilityRoutes);
};
