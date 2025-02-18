import { useRoutes } from 'react-router-dom';
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
      path: 'grievance/new-ticket',
      element: <CreateGrievancePage />,
    },
    {
      path: 'grievance/edit-ticket/user-generated/:id',
      element: <EditGrievancePage />,
    },
    {
      path: 'grievance/edit-ticket/system-generated/:id',
      element: <EditGrievancePage />,
    },
    {
      path: 'grievance/tickets/user-generated/:id',
      element: <GrievancesDetailsPage />,
    },
    {
      path: 'grievance/tickets/system-generated/:id',
      element: <GrievancesDetailsPage />,
    },
    {
      path: 'grievance/rdi/:id',
      element: <GrievancesTablePage />,
    },
    {
      path: 'grievance/payment-verification/:cashPlanId',
      element: <GrievancesTablePage />,
    },
    {
      path: 'grievance/tickets/user-generated',
      element: <GrievancesTablePage />,
    },
    {
      path: 'grievance/tickets/system-generated',
      element: <GrievancesTablePage />,
    },
    {
      path: 'grievance/dashboard',
      element: <GrievancesDashboardPage />,
    },
    {
      path: 'grievance/feedback/create',
      element: <CreateFeedbackPage />,
    },
    {
      path: 'grievance/feedback/edit-ticket/:id',
      element: <EditFeedbackPage />,
    },
    {
      path: 'grievance/feedback/:id',
      element: <FeedbackDetailsPage />,
    },
    {
      path: 'grievance/feedback',
      element: <FeedbackPage />,
    },
  ];

  return useRoutes(grievanceRoutes);
};
