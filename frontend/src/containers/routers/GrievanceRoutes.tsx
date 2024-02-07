import * as React from 'react';
import { Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '@components/core/SentryRoute';
import { CreateFeedbackPage } from '../pages/accountability/feedback/CreateFeedbackPage';
import { EditFeedbackPage } from '../pages/accountability/feedback/EditFeedbackPage';
import { FeedbackDetailsPage } from '../pages/accountability/feedback/FeedbackDetailsPage';
import { FeedbackPage } from '../pages/accountability/feedback/FeedbackPage';
import { CreateGrievancePage } from '../pages/grievances/CreateGrievancePage';
import { EditGrievancePage } from '../pages/grievances/EditGrievancePage';
import { GrievancesDashboardPage } from '../pages/grievances/GrievancesDashboardPage';
import { GrievancesDetailsPage } from '../pages/grievances/GrievancesDetailsPage/GrievancesDetailsPage';
import { GrievancesTablePage } from '../pages/grievances/GrievancesTablePage';

export function GrievanceRoutes(): React.ReactElement {
  const { path } = useRouteMatch();

  const grievanceRoutes = [
    {
      path: `${path}/grievance/new-ticket`,
      component: <CreateGrievancePage />,
    },
    {
      path: `${path}/grievance/edit-ticket/user-generated/:id`,
      component: <EditGrievancePage key="user" />,
    },
    {
      path: `${path}/grievance/edit-ticket/system-generated/:id`,
      component: <EditGrievancePage key="system" />,
    },
    {
      path: `${path}/grievance/tickets/user-generated/:id`,
      component: <GrievancesDetailsPage key="user" />,
    },
    {
      path: `${path}/grievance/tickets/system-generated/:id`,
      component: <GrievancesDetailsPage key="system" />,
    },
    {
      path: `${path}/grievance/rdi/:id`,
      component: <GrievancesTablePage key="rdi" />,
    },
    {
      path: `${path}/grievance/payment-verification/:cashPlanId`,
      component: <GrievancesTablePage key="verificationId" />,
    },
    {
      path: `${path}/grievance/tickets/user-generated`,
      component: <GrievancesTablePage key="user" />,
    },
    {
      path: `${path}/grievance/tickets/system-generated`,
      component: <GrievancesTablePage key="system" />,
    },
    {
      path: `${path}/grievance/dashboard`,
      component: <GrievancesDashboardPage key="all" />,
    },
    {
      path: `${path}/grievance/feedback/create`,
      component: <CreateFeedbackPage />,
    },
    {
      path: `${path}/grievance/feedback/edit-ticket/:id`,
      component: <EditFeedbackPage />,
    },
    {
      path: `${path}/grievance/feedback/:id`,
      component: <FeedbackDetailsPage />,
    },
    {
      path: `${path}/grievance/feedback`,
      component: <FeedbackPage />,
    },
  ];

  return (
    <Switch>
      {grievanceRoutes.map((route) => (
        <SentryRoute key={route.path} path={route.path}>
          {route.component}
        </SentryRoute>
      ))}
    </Switch>
  );
}
