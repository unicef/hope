import React from 'react';
import styled from 'styled-components';
import { makeStyles, Snackbar, SnackbarContent } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { Route, Switch, useLocation } from 'react-router-dom';
import * as Sentry from '@sentry/react';
import { MiśTheme } from '../theme';
import { Drawer } from '../components/Drawer/Drawer';
import { AppBar } from '../components/AppBar';
import { useSnackbar } from '../hooks/useSnackBar';
import { GrievanceDetailsPage } from '../components/Grievances/GrievancesDetailsPage/GrievanceDetailsPage';
import { GrievancesTablePage } from '../components/Grievances/GrievancesTablePage';
import { CreateGrievancePage } from '../components/Grievances/CreateGrievancePage';
import { EditGrievancePage } from '../components/Grievances/EditGrievancePage';
import { DashboardPage } from './pages/DashboardPage';
import { ProgramsPage } from './pages/ProgramsPage';
import { ProgramDetailsPage } from './pages/ProgramDetailsPage';
import { CashPlanDetailsPage } from './pages/CashPlanDetailsPage';
import { PaymentRecordDetailsPage } from './pages/PaymentRecordDetailsPage';
import { PopulationHouseholdPage } from './pages/PopulationHouseholdPage';
import { RegistrationDataImportPage } from './registration/list/RegistrationDataImportPage';
import { PopulationHouseholdDetailsPage } from './pages/PopulationHouseholdDetailsPage';
import { PopulationIndividualsPage } from './pages/PopulationIndividualsPage';
import { PopulationIndividualsDetailsPage } from './pages/PopulationIndividualsDetailsPage';
import { TargetPopulationPage } from './pages/TargetPopulationPage';
import { TargetPopulationDetailsPage } from './pages/TargetPopulationDetailsPage';
import { CreateTargetPopulation } from './pages/CreateTargetPopulation';
import { RegistrationDataImportDetailsPage } from './registration/details/RegistrationDataImportDetailsPage';
import { RegistrationHouseholdDetailsPage } from './registration/details/households/RegistrationHouseholdDetailsPage';
import { RegistrationIndividualDetailsPage } from './registration/details/individual/RegistrationIndividualDetailsPage';
import { PaymentVerificationPage } from './pages/PaymentVerificationPage';
import { PaymentVerificationDetailsPage } from './pages/PaymentVerificationDetailsPage';
import { VerificationRecordDetailsPage } from './pages/VerificationRecordDetailsPage';
import { UsersList } from './pages/UsersList';
import { ReportingPage } from './pages/ReportingPage';
import { ReportingDetailsPage } from './pages/ReportingDetailsPage';
import { ActivityLogPage } from './pages/MainActivityLogPage';
import { CashPlanVerificationRedirectPage } from './pages/CashplanVerificationRedirectPage';

const Root = styled.div`
  display: flex;
`;
const MainContent = styled.div`
  flex-grow: 1;
  height: 100vh;
  overflow: auto;
`;
const useStyles = makeStyles((theme: MiśTheme) => ({
  appBarSpacer: theme.mixins.toolbar,
}));

export function HomeRouter(): React.ReactElement {
  const [open, setOpen] = React.useState(true);
  const classes = useStyles({});
  const location = useLocation();
  const snackBar = useSnackbar();
  const handleDrawerOpen = (): void => {
    setOpen(true);
  };
  const handleDrawerClose = (): void => {
    setOpen(false);
  };
  return (
    <Root>
      <CssBaseline />
      <AppBar open={open} handleDrawerOpen={handleDrawerOpen} />
      <Drawer
        open={open}
        handleDrawerClose={handleDrawerClose}
        currentLocation={location.pathname}
        dataCy='side-nav'
      />
      <MainContent data-cy='main-content'>
        <div className={classes.appBarSpacer} />
        <Switch>
          <Route path='/:businessArea/population/household/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/population/household/:id');
              }}
            >
              <PopulationHouseholdDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/population/individuals/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/population/individuals/:id');
              }}
            >
              <PopulationIndividualsDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/cashplans/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/cashplans/:id');
              }}
            >
              <CashPlanDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>

          <Route exact path='/:businessArea/target-population'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/target-population');
              }}
            >
              <TargetPopulationPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/target-population/create'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/target-population/create');
              }}
            >
              <CreateTargetPopulation />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/target-population/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/target-population/:id');
              }}
            >
              <TargetPopulationDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route exact path='/:businessArea/payment-verification'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/payment-verification');
              }}
            >
              <PaymentVerificationPage />
            </Sentry.ErrorBoundary>
          </Route>

          <Route path='/:businessArea/verification-records/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/verification-records/:id');
              }}
            >
              <VerificationRecordDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/payment-verification/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/payment-verification/:id');
              }}
            >
              <PaymentVerificationDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/csh-payment-verification/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/csh-payment-verification/:id');
              }}
            >
              <CashPlanVerificationRedirectPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/grievance-and-feedback/new-ticket'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/grievance-and-feedback/new-ticket');
              }}
            >
              <CreateGrievancePage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/grievance-and-feedback/edit-ticket/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag(
                  'location',
                  '/grievance-and-feedback/edit-ticket/:id',
                );
              }}
            >
              <EditGrievancePage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/grievance-and-feedback/rdi/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag(
                  'location',
                  '/:businessArea/grievance-and-feedback',
                );
              }}
            >
              <GrievancesTablePage key='rdi' />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/grievance-and-feedback/payment-verification/:verificationId'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag(
                  'location',
                  '/:businessArea/grievance-and-feedback',
                );
              }}
            >
              <GrievancesTablePage key='verificationId' />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/grievance-and-feedback/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/grievance-and-feedback/:id');
              }}
            >
              <GrievanceDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/grievance-and-feedback'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag(
                  'location',
                  '/:businessArea/grievance-and-feedback',
                );
              }}
            >
              <GrievancesTablePage key='all' />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/population/household'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/population/household');
              }}
            >
              <PopulationHouseholdPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/population/individuals'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/population/individuals');
              }}
            >
              <PopulationIndividualsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/programs/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/programs/:id');
              }}
            >
              <ProgramDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/payment-records/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/payment-records/:id');
              }}
            >
              <PaymentRecordDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/programs'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/programs');
              }}
            >
              <ProgramsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/registration-data-import/household/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag(
                  'location',
                  '/registration-data-import/household/:id',
                );
              }}
            >
              <RegistrationHouseholdDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/registration-data-import/individual/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag(
                  'location',
                  '/registration-data-import/individual/:id',
                );
              }}
            >
              <RegistrationIndividualDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/registration-data-import/:id'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/registration-data-import/:id');
              }}
            >
              <RegistrationDataImportDetailsPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/registration-data-import'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/registration-data-import');
              }}
            >
              <RegistrationDataImportPage />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/reporting/:id'>
            <ReportingDetailsPage />
          </Route>
          <Route path='/:businessArea/reporting'>
            <ReportingPage />
          </Route>
          <Route path='/:businessArea/users-list'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/users-list');
              }}
            >
              <UsersList />
            </Sentry.ErrorBoundary>
          </Route>
          <Route path='/:businessArea/activity-log'>
            <ActivityLogPage />
          </Route>
          <Route path='/:businessArea'>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', '/ - Dashboard');
              }}
            >
              <DashboardPage />
            </Sentry.ErrorBoundary>
          </Route>
        </Switch>
      </MainContent>
      {snackBar.show && (
        <Snackbar
          open={snackBar.show}
          autoHideDuration={5000}
          onClose={() => snackBar.setShow(false)}
        >
          <SnackbarContent
            message={snackBar.message}
            data-cy={snackBar.dataCy}
          />
        </Snackbar>
      )}
    </Root>
  );
}
