import { useRoutes, Navigate } from 'react-router-dom';
import EditFeedbackPage from '../pages/accountability/feedback/EditFeedbackPage';
import CreateGrievancePage from '../pages/grievances/CreateGrievancePage';
import EditGrievancePage from '../pages/grievances/EditGrievancePage';
import GrievancesDetailsPage from '../pages/grievances/GrievancesDetailsPage/GrievancesDetailsPage';
import GrievancesTablePage from '../pages/grievances/GrievancesTablePage';
import { ReactElement } from 'react';
import CreateFeedbackPage from '@containers/pages/accountability/feedback/CreateFeedbackPage';
import FeedbackDetailsPage from '@containers/pages/accountability/feedback/FeedbackDetailsPage';
import FeedbackPage from '@containers/pages/accountability/feedback/FeedbackPage';
import GrievancesDashboardPage from '@containers/pages/grievances/GrievancesDashboardPage';

export const GrievanceRoutes = (): ReactElement => {
  const grievanceRoutes = [
    {
      path: 'grievance',
      children: [
        {
          path: 'new-ticket',
          element: <CreateGrievancePage />,
        },
        {
          path: 'edit-ticket/user-generated/:id',
          element: <EditGrievancePage />,
        },
        {
          path: 'edit-ticket/system-generated/:id',
          element: <EditGrievancePage />,
        },
        {
          path: 'tickets/user-generated/:id',
          element: <GrievancesDetailsPage />,
        },
        {
          path: 'tickets/system-generated/:id',
          element: <GrievancesDetailsPage />,
        },
        {
          path: 'rdi/:id',
          element: <GrievancesTablePage />,
        },
        {
          path: 'payment-verification/:cashPlanId',
          element: <GrievancesTablePage />,
        },
        {
          path: 'tickets/user-generated',
          element: <GrievancesTablePage />,
        },
        {
          path: 'tickets/system-generated',
          element: <GrievancesTablePage />,
        },
        {
          path: 'dashboard',
          element: <GrievancesDashboardPage />,
        },
        {
          path: 'feedback/create',
          element: <CreateFeedbackPage />,
        },
        {
          path: 'feedback/edit-ticket/:id',
          element: <EditFeedbackPage />,
        },
        {
          path: 'feedback/:id',
          element: <FeedbackDetailsPage />,
        },
        {
          path: 'feedback',
          element: <FeedbackPage />,
        },
        {
          path: '*',
          element: <Navigate to="/404" replace />,
        },
      ],
    },
  ];

  return useRoutes(grievanceRoutes);
};
