import * as React from 'react';
import { useLocation, useRoutes } from 'react-router-dom';
import { CreateFeedbackPage } from '../pages/accountability/feedback/CreateFeedbackPage';
import { EditFeedbackPage } from '../pages/accountability/feedback/EditFeedbackPage';
import { FeedbackDetailsPage } from '../pages/accountability/feedback/FeedbackDetailsPage';
import { FeedbackPage } from '../pages/accountability/feedback/FeedbackPage';
import { CreateGrievancePage } from '../pages/grievances/CreateGrievancePage';
import { EditGrievancePage } from '../pages/grievances/EditGrievancePage';
import { GrievancesDashboardPage } from '../pages/grievances/GrievancesDashboardPage';
import { GrievancesDetailsPage } from '../pages/grievances/GrievancesDetailsPage/GrievancesDetailsPage';
import { GrievancesTablePage } from '../pages/grievances/GrievancesTablePage';

export const GrievanceRoutes = (): React.ReactElement => {
  const location = useLocation();
  const path = location.pathname;

  const grievanceRoutes = [
    {
      path: `${path}/grievance/new-ticket`,
      element: <CreateGrievancePage />,
    },
    {
      path: `${path}/grievance/edit-ticket/user-generated/:id`,
      element: <EditGrievancePage />,
    },
    {
      path: `${path}/grievance/edit-ticket/system-generated/:id`,
      element: <EditGrievancePage />,
    },
    {
      path: `${path}/grievance/tickets/user-generated/:id`,
      element: <GrievancesDetailsPage />,
    },
    {
      path: `${path}/grievance/tickets/system-generated/:id`,
      element: <GrievancesDetailsPage />,
    },
    {
      path: `${path}/grievance/rdi/:id`,
      element: <GrievancesTablePage />,
    },
    {
      path: `${path}/grievance/payment-verification/:cashPlanId`,
      element: <GrievancesTablePage />,
    },
    {
      path: `${path}/grievance/tickets/user-generated`,
      element: <GrievancesTablePage />,
    },
    {
      path: `${path}/grievance/tickets/system-generated`,
      element: <GrievancesTablePage />,
    },
    {
      path: `${path}/grievance/dashboard`,
      element: <GrievancesDashboardPage />,
    },
    {
      path: `${path}/grievance/feedback/create`,
      element: <CreateFeedbackPage />,
    },
    {
      path: `${path}/grievance/feedback/edit-ticket/:id`,
      element: <EditFeedbackPage />,
    },
    {
      path: `${path}/grievance/feedback/:id`,
      element: <FeedbackDetailsPage />,
    },
    {
      path: `${path}/grievance/feedback`,
      element: <FeedbackPage />,
    },
  ];

  return useRoutes(grievanceRoutes);
};
