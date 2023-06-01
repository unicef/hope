import { makeStyles, Snackbar, SnackbarContent } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import React from 'react';
import { Redirect, Switch, useLocation, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { AppBar } from '../components/core/AppBar';
import { Drawer } from '../components/core/Drawer/Drawer';
import { LoadingComponent } from '../components/core/LoadingComponent';
import { SentryRoute } from '../components/core/SentryRoute';
import { useSnackbar } from '../hooks/useSnackBar';
import { MiśTheme } from '../theme';
import { useAllBusinessAreasQuery } from '../__generated__/graphql';
import { ActivityLogPage } from './pages/core/MainActivityLogPage';
import { UsersPage } from './pages/core/UsersPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { CreateGrievancePage } from './pages/grievances/CreateGrievancePage';
import { EditGrievancePage } from './pages/grievances/EditGrievancePage';
import { GrievancesDashboardPage } from './pages/grievances/GrievancesDashboardPage';
import { GrievancesDetailsPage } from './pages/grievances/GrievancesDetailsPage/GrievancesDetailsPage';
import { GrievancesTablePage } from './pages/grievances/GrievancesTablePage';
import { CommunicationPage } from './pages/accountability/communication/CommunicationPage';
import { CommunicationDetailsPage } from './pages/accountability/communication/CommunicationDetailsPage';
import { CreateCommunicationPage } from './pages/accountability/communication/CreateCommunicationPage';
import { CreatePaymentPlanPage } from './pages/paymentmodule/CreatePaymentPlanPage';
import { EditPaymentPlanPage } from './pages/paymentmodule/EditPaymentPlanPage';
import { EditSetUpFspPage } from './pages/paymentmodule/EditSetUpFspPage';
import { PaymentDetailsPage } from './pages/paymentmodule/PaymentDetailsPage';
import { PaymentModulePage } from './pages/paymentmodule/PaymentModulePage';
import { PaymentPlanDetailsPage } from './pages/paymentmodule/PaymentPlanDetailsPage';
import { SetUpFspPage } from './pages/paymentmodule/SetUpFspPage';
import { CashPlanDetailsPage } from './pages/payments/CashPlanDetailsPage';
import { CashPlanVerificationDetailsPage } from './pages/payments/CashPlanVerificationDetailsPage';
import { CashPlanVerificationRedirectPage } from './pages/payments/CashplanVerificationRedirectPage';
import { PaymentPlanVerificationDetailsPage } from './pages/payments/PaymentPlanVerificationDetailsPage';
import { PaymentRecordDetailsPage } from './pages/payments/PaymentRecordDetailsPage';
import { PaymentVerificationPage } from './pages/payments/PaymentVerificationPage';
import { VerificationPaymentDetailsPage } from './pages/payments/VerificationPaymentDetailsPage';
import { VerificationPaymentRecordDetailsPage } from './pages/payments/VerificationPaymentRecordDetailsPage';
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
import { EditTargetPopulationPage } from './pages/targeting/EditTargetPopulationPage';
import { TargetPopulationDetailsPage } from './pages/targeting/TargetPopulationDetailsPage';
import { TargetPopulationsPage } from './pages/targeting/TargetPopulationsPage';
import { FeedbackPage } from './pages/accountability/feedback/FeedbackPage';
import { FeedbackDetailsPage } from './pages/accountability/feedback/FeedbackDetailsPage';
import { CreateFeedbackPage } from './pages/accountability/feedback/CreateFeedbackPage';
import { EditFeedbackPage } from './pages/accountability/feedback/EditFeedbackPage';
import { SurveysPage } from './pages/accountability/surveys/SurveysPage';
import { CreateSurveyPage } from './pages/accountability/surveys/CreateSurveyPage';
import { SurveyDetailsPage } from './pages/accountability/surveys/SurveyDetailsPage';
import { FollowUpPaymentPlanDetailsPage } from './pages/paymentmodule/FollowUpPaymentPlanDetailsPage';
import { SetFollowUpUpFspPage } from './pages/paymentmodule/SetFollowUpUpFspPage';
import { EditFollowUpSetUpFspPage } from './pages/paymentmodule/EditFollowUpSetUpFspPage';
import { EditFollowUpPaymentPlanPage } from './pages/paymentmodule/EditFollowUpPaymentPlanPage';

const Root = styled.div`
  display: flex;
`;
const MainContent = styled.div`
  flex-grow: 1;
  overflow: auto;
`;
const useStyles = makeStyles((theme: MiśTheme) => ({
  appBarSpacer: theme.mixins.toolbar,
}));

export function HomeRouter(): React.ReactElement {
  const [open, setOpen] = React.useState(true);
  const { businessArea } = useParams();
  const classes = useStyles({});
  const location = useLocation();
  const snackBar = useSnackbar();
  const handleDrawerOpen = (): void => {
    setOpen(true);
  };
  const handleDrawerClose = (): void => {
    setOpen(false);
  };
  const { data, loading } = useAllBusinessAreasQuery({
    variables: {
      slug: businessArea,
    },
    fetchPolicy: 'cache-first',
  });

  if (!data) {
    return null;
  }

  if (loading) {
    return <LoadingComponent />;
  }
  const allBusinessAreasSlugs = data.allBusinessAreas.edges.map(
    (el) => el.node.slug,
  );
  const isBusinessAreaValid = allBusinessAreasSlugs.includes(businessArea);

  if (!isBusinessAreaValid) {
    return <Redirect to='/' noThrow />;
  }

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
          <SentryRoute path='/:businessArea/target-population/edit-tp/:id'>
            <EditTargetPopulationPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/target-population/:id'>
            <TargetPopulationDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/verification/payment-record/:id'>
            <VerificationPaymentRecordDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/verification/payment/:id'>
            <VerificationPaymentDetailsPage />
          </SentryRoute>
          <SentryRoute exact path='/:businessArea/payment-verification'>
            <PaymentVerificationPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-verification/cash-plan/:id'>
            <CashPlanVerificationDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-verification/payment-plan/:id'>
            <PaymentPlanVerificationDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/csh-payment-verification/:id'>
            <CashPlanVerificationRedirectPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/new-plan'>
            <CreatePaymentPlanPage />
          </SentryRoute>
          <SentryRoute exact path='/:businessArea/payment-module'>
            <PaymentModulePage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/followup-payment-plans/:id/edit'>
            <EditFollowUpPaymentPlanPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/followup-payment-plans/:id/setup-fsp/create'>
            <SetFollowUpUpFspPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/followup-payment-plans/:id/setup-fsp/edit'>
            <EditFollowUpSetUpFspPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/payment-plans/:id/setup-fsp/create'>
            <SetUpFspPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/payment-plans/:id/setup-fsp/edit'>
            <EditSetUpFspPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/payment-plans/:id/edit'>
            <EditPaymentPlanPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/payments/:id'>
            <PaymentDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/payment-plans/:id'>
            <PaymentPlanDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/payment-module/followup-payment-plans/:id'>
            <FollowUpPaymentPlanDetailsPage />
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
          <SentryRoute path='/:businessArea/grievance-and-feedback/tickets'>
            <GrievancesTablePage key='all' />
          </SentryRoute>
          <SentryRoute path='/:businessArea/grievance-and-feedback/dashboard'>
            <GrievancesDashboardPage key='all' />
          </SentryRoute>
          <SentryRoute path='/:businessArea/grievance-and-feedback/:id'>
            <GrievancesDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/communication/create'>
            <CreateCommunicationPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/communication/:id'>
            <CommunicationDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/communication'>
            <CommunicationPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/feedback/create'>
            <CreateFeedbackPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/feedback/edit-ticket/:id'>
            <EditFeedbackPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/feedback/:id'>
            <FeedbackDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/feedback'>
            <FeedbackPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/surveys/create'>
            <CreateSurveyPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/surveys/:id'>
            <SurveyDetailsPage />
          </SentryRoute>
          <SentryRoute path='/:businessArea/accountability/surveys'>
            <SurveysPage />
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
