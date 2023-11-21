import React from 'react';
import { Redirect, Switch, useRouteMatch } from 'react-router-dom';
import { SentryRoute } from '../../components/core/SentryRoute';
import { ProgramsPage } from '../pages/program/ProgramsPage';
import { ProgramDetailsPage } from '../pages/program/ProgramDetailsPage';
import { DashboardPage } from '../pages/dashboard/DashboardPage';
import { ActivityLogPage } from '../pages/core/MainActivityLogPage';
import { CreateGrievancePage } from '../pages/grievances/CreateGrievancePage';
import { EditGrievancePage } from '../pages/grievances/EditGrievancePage';
import { GrievancesDashboardPage } from '../pages/grievances/GrievancesDashboardPage';
import { GrievancesDetailsPage } from '../pages/grievances/GrievancesDetailsPage/GrievancesDetailsPage';
import { GrievancesTablePage } from '../pages/grievances/GrievancesTablePage';
import { ReportingPage } from '../pages/reporting/ReportingPage';
import { CreateFeedbackPage } from '../pages/accountability/feedback/CreateFeedbackPage';
import { EditFeedbackPage } from '../pages/accountability/feedback/EditFeedbackPage';
import { FeedbackDetailsPage } from '../pages/accountability/feedback/FeedbackDetailsPage';
import { FeedbackPage } from '../pages/accountability/feedback/FeedbackPage';
import { ReportingDetailsPage } from '../pages/reporting/ReportingDetailsPage';
import { CreateProgramPage } from '../pages/program/CreateProgramPage';
import { EditProgramPage } from '../pages/program/EditProgramPage';

export const AllProgramsRoutesSwitch = (): React.ReactElement => {
  const { path } = useRouteMatch();
  return (
    <Switch>
      <SentryRoute label='/ - Dashboard' path={`${path}/country-dashboard`}>
        <DashboardPage />
      </SentryRoute>
      <SentryRoute path={`${path}/create`}>
        <CreateProgramPage />
      </SentryRoute>
      <SentryRoute path={`${path}/edit/:id`}>
        <EditProgramPage />
      </SentryRoute>
      <SentryRoute path={`${path}/list`}>
        <ProgramsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/details/:id`}>
        <ProgramDetailsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/reporting/:id`}>
        <ReportingDetailsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/reporting`}>
        <ReportingPage />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/new-ticket`}>
        <CreateGrievancePage />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/edit-ticket/user-generated/:id`}>
        <EditGrievancePage key='user' />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/edit-ticket/system-generated/:id`}>
        <EditGrievancePage key='system' />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/tickets/user-generated/:id`}>
        <GrievancesDetailsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/tickets/system-generated/:id`}>
        <GrievancesDetailsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/tickets/user-generated`}>
        <GrievancesTablePage key='user' />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/tickets/system-generated`}>
        <GrievancesTablePage key='system' />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/dashboard`}>
        <GrievancesDashboardPage key='all' />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/feedback/create`}>
        <CreateFeedbackPage />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/feedback/edit-ticket/:id`}>
        <EditFeedbackPage />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/feedback/:id`}>
        <FeedbackDetailsPage />
      </SentryRoute>
      <SentryRoute path={`${path}/grievance/feedback`}>
        <FeedbackPage />
      </SentryRoute>
      <SentryRoute path={`${path}/activity-log`}>
        <ActivityLogPage />
      </SentryRoute>
      <SentryRoute path={`${path}/`}>
        <Redirect to='/' />
      </SentryRoute>
    </Switch>
  );
};
