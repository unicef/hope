import { makeStyles, Snackbar, SnackbarContent } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import React from 'react';
import { Switch, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { AppBar } from '../components/core/AppBar';
import { Drawer } from '../components/core/Drawer/Drawer';
import { SentryRoute } from '../components/core/SentryRoute';
import { useSnackbar } from '../hooks/useSnackBar';
import { MiśTheme } from '../theme';
import { ActivityLogPage } from './pages/core/MainActivityLogPage';
import { UsersPage } from './pages/core/UsersPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { CreateGrievancePage } from './pages/grievances/CreateGrievancePage';
import { EditGrievancePage } from './pages/grievances/EditGrievancePage';
import { GrievancesDetailsPage } from './pages/grievances/GrievancesDetailsPage/GrievancesDetailsPage';
import { GrievancesTablePage } from './pages/grievances/GrievancesTablePage';
import { CashPlanDetailsPage } from './pages/payments/CashPlanDetailsPage';
import { CashPlanVerificationRedirectPage } from './pages/payments/CashplanVerificationRedirectPage';
import { PaymentRecordDetailsPage } from './pages/payments/PaymentRecordDetailsPage';
import { PaymentVerificationDetailsPage } from './pages/payments/PaymentVerificationDetailsPage';
import { PaymentVerificationPage } from './pages/payments/PaymentVerificationPage';
import { VerificationRecordDetailsPage } from './pages/payments/VerificationRecordDetailsPage';
import { PopulationHouseholdDetailsPage } from './pages/population/PopulationHouseholdDetailsPage';
import { PopulationHouseholdPage } from './pages/population/PopulationHouseholdPage';
import { PopulationIndividualsDetailsPage } from './pages/population/PopulationIndividualsDetailsPage';
import { PopulationIndividualsPage } from './pages/population/PopulationIndividualsPage';
import { ProgramDetailsPage } from './pages/program/ProgramDetailsPage';
import { ProgramsPage } from './pages/program/ProgramsPage';
import { RegistrationDataImportDetailsPage } from './pages/rdi/RegistrationDataImportDetailsPage';
import { RegistrationDataImportPage } from './pages/rdi/RegistrationDataImportPage';
import { RegistrationHouseholdDetailsPage } from './pages/rdi/RegistrationHouseholdDetailsPage';
import { RegistrationIndividualDetailsPage } from './pages/rdi/RegistrationIndividualDetailsPage';
import { ReportingDetailsPage } from './pages/reporting/ReportingDetailsPage';
import { ReportingPage } from './pages/reporting/ReportingPage';
import { CreateTargetPopulationPage } from './pages/targeting/CreateTargetPopulationPage';
import { TargetPopulationDetailsPage } from './pages/targeting/TargetPopulationDetailsPage';
import { TargetPopulationsPage } from './pages/targeting/TargetPopulationsPage';
import { PaymentModulePage } from './pages/paymentmodule/PaymentModulePage';
import { CreatePaymentPlanPage } from './pages/paymentmodule/CreatePaymentPlanPage';
import { CreateFspPage } from './pages/paymentmodule/CreateFspPage';
import { EditFspPage } from './pages/paymentmodule/EditFspPage';
import { CreateSetUpFspPage } from './pages/paymentmodule/CreateSetUpFspPage';
import { EditSetUpFspPage } from './pages/paymentmodule/EditSetUpFspPage';
import { PaymentPlanDetailsPage } from './pages/paymentmodule/PaymentPlanDetailsPage';
import { EditPaymentPlanPage } from './pages/paymentmodule/EditPaymentPlanPage';
import { SetUpFspPage } from './pages/paymentmodule/SetUpFspPage';

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
          <SentryRoute path='/:businessArea/population/household/:id'>
            <PopulationHouseholdDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/population/individuals/:id'>
            <PopulationIndividualsDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/cashplans/:id'>
            <CashPlanDetailsPage />
          </SentryRoute>
          <SentryRoute exact path='/:businessArea/target-population'>
            <TargetPopulationsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/target-population/create'>
            <CreateTargetPopulationPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/target-population/:id'>
            <TargetPopulationDetailsPage />
          </SentryRoute>
          <SentryRoute exact path='/:businessArea/payment-verification'>
            <PaymentVerificationPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/verification-records/:id'>
            <VerificationRecordDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-verification/:id'>
            <PaymentVerificationDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/csh-payment-verification/:id'>
            <CashPlanVerificationRedirectPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/new-plan'>
            <CreatePaymentPlanPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/new-fsp'>
            <CreateFspPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/fsp/:id'>
            <EditFspPage />
          </SentryRoute>
          <SentryRoute exact path='/:businessArea/payment-module'>
            <PaymentModulePage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/payment-plans/:id/setup-fsp/edit'>
            <EditSetUpFspPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/payment-plans/:id/edit'>
            <EditPaymentPlanPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/payment-plans/:id'>
            <PaymentPlanDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/grievance-and-feedback/new-ticket'>
            <CreateGrievancePage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/grievance-and-feedback/edit-ticket/:id'>
            <EditGrievancePage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/grievance-and-feedback/rdi/:id'>
            <GrievancesTablePage key='rdi' />
          </SentryRoute>
          <SentryRoute path='/:businessArea/grievance-and-feedback/payment-verification/:cashPlanId'>
            <GrievancesTablePage key='verificationId' />
          </SentryRoute>
          <SentryRoute path='/:businessArea/grievance-and-feedback/:id'>
            <GrievancesDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/grievance-and-feedback'>
            <GrievancesTablePage key='all' />
          </SentryRoute>
          <SentryRoute path='/:businessArea/population/household'>
            <PopulationHouseholdPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/population/individuals'>
            <PopulationIndividualsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/programs/:id'>
            <ProgramDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-records/:id'>
            <PaymentRecordDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/programs'>
            <ProgramsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/registration-data-import/household/:id'>
            <RegistrationHouseholdDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/registration-data-import/individual/:id'>
            <RegistrationIndividualDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/registration-data-import/:id'>
            <RegistrationDataImportDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/registration-data-import'>
            <RegistrationDataImportPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/reporting/:id'>
            <ReportingDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/reporting'>
            <ReportingPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/users-list'>
            <UsersPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/activity-log'>
            <ActivityLogPage />
          </SentryRoute>
          <SentryRoute label='/ - Dashboard' path='/:businessArea'>
            <DashboardPage />
          </SentryRoute>
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
