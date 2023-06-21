import { makeStyles, Snackbar, SnackbarContent } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import React from 'react';
import {
  Redirect,
  Switch,
  useHistory,
  useLocation,
  useRouteMatch,
} from 'react-router-dom';
import styled from 'styled-components';
import {
  useAllBusinessAreasQuery,
  useAllProgramsForChoicesQuery,
} from '../__generated__/graphql';
import { AppBar } from '../components/core/AppBar';
import { Drawer } from '../components/core/Drawer/Drawer';
import { LoadingComponent } from '../components/core/LoadingComponent';
import { SentryRoute } from '../components/core/SentryRoute';
import { useBaseUrl } from '../hooks/useBaseUrl';
import { useSnackbar } from '../hooks/useSnackBar';
import { MiśTheme } from '../theme';
import { CreateFeedbackPage } from './pages/accountability/feedback/CreateFeedbackPage';
import { EditFeedbackPage } from './pages/accountability/feedback/EditFeedbackPage';
import { FeedbackDetailsPage } from './pages/accountability/feedback/FeedbackDetailsPage';
import { FeedbackPage } from './pages/accountability/feedback/FeedbackPage';
import { ActivityLogPage } from './pages/core/MainActivityLogPage';
import { UsersPage } from './pages/core/UsersPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { CreateGrievancePage } from './pages/grievances/CreateGrievancePage';
import { EditGrievancePage } from './pages/grievances/EditGrievancePage';
import { GrievancesDashboardPage } from './pages/grievances/GrievancesDashboardPage';
import { GrievancesDetailsPage } from './pages/grievances/GrievancesDetailsPage/GrievancesDetailsPage';
import { GrievancesTablePage } from './pages/grievances/GrievancesTablePage';
import { CreatePaymentPlanPage } from './pages/paymentmodule/CreatePaymentPlanPage';
import { EditFollowUpPaymentPlanPage } from './pages/paymentmodule/EditFollowUpPaymentPlanPage';
import { EditFollowUpSetUpFspPage } from './pages/paymentmodule/EditFollowUpSetUpFspPage';
import { EditPaymentPlanPage } from './pages/paymentmodule/EditPaymentPlanPage';
import { EditSetUpFspPage } from './pages/paymentmodule/EditSetUpFspPage';
import { FollowUpPaymentPlanDetailsPage } from './pages/paymentmodule/FollowUpPaymentPlanDetailsPage';
import { PaymentDetailsPage } from './pages/paymentmodule/PaymentDetailsPage';
import { PaymentModulePage } from './pages/paymentmodule/PaymentModulePage';
import { PaymentPlanDetailsPage } from './pages/paymentmodule/PaymentPlanDetailsPage';
import { SetFollowUpUpFspPage } from './pages/paymentmodule/SetFollowUpUpFspPage';
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

const Root = styled.div`
  display: flex;
  max-width: 100%;
  overflow-x: hidden;
`;
const MainContent = styled.div`
  flex-grow: 1;
  overflow: auto;
  max-width: 100%;
  overflow-x: hidden;
`;
const useStyles = makeStyles((theme: MiśTheme) => ({
  appBarSpacer: theme.mixins.toolbar,
}));

export const HomeRouter = (): React.ReactElement => {
  const [open, setOpen] = React.useState(true);
  const { businessArea } = useBaseUrl();
  const classes = useStyles({});
  const location = useLocation();
  const { path } = useRouteMatch();
  const snackBar = useSnackbar();
  const handleDrawerOpen = (): void => {
    setOpen(true);
  };
  const handleDrawerClose = (): void => {
    setOpen(false);
  };
  const {
    data: businessAreaData,
    loading: businessAreaLoading,
  } = useAllBusinessAreasQuery({
    variables: {
      slug: businessArea,
    },
    fetchPolicy: 'cache-first',
  });

  const {
    data: programsData,
    loading: programsLoading,
  } = useAllProgramsForChoicesQuery({
    variables: { businessArea, first: 100 },
    fetchPolicy: 'cache-first',
  });

  if (!businessAreaData) {
    return null;
  }

  if (businessAreaLoading) {
    return <LoadingComponent />;
  }

  if (!businessAreaData || !programsData) {
    return null;
  }

  if (businessAreaLoading || programsLoading) {
    return <LoadingComponent />;
  }
  const allBusinessAreasSlugs = businessAreaData.allBusinessAreas.edges.map(
    (el) => el.node.slug,
  );
  // const allProgramsIds = programsData.allPrograms.edges.map((el) => el.node.id);
  const isBusinessAreaValid = allBusinessAreasSlugs.includes(businessArea);
  // const isProgramValid = allProgramsIds.includes(programId);

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
          <SentryRoute path={`${path}/population/household/:id`}>
            <PopulationHouseholdDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/population/individuals/:id`}>
            <PopulationIndividualsDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/cashplans/:id`}>
            <CashPlanDetailsPage />
          </SentryRoute>
          <SentryRoute exact path={`${path}/target-population`}>
            <TargetPopulationsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/target-population/create`}>
            <CreateTargetPopulationPage />
          </SentryRoute>
          <SentryRoute path={`${path}/target-population/edit-tp/:id`}>
            <EditTargetPopulationPage />
          </SentryRoute>
          <SentryRoute path={`${path}/target-population/:id`}>
            <TargetPopulationDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/verification/payment-record/:id`}>
            <VerificationPaymentRecordDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/verification/payment/:id`}>
            <VerificationPaymentDetailsPage />
          </SentryRoute>
          <SentryRoute exact path={`${path}/payment-verification`}>
            <PaymentVerificationPage />
          </SentryRoute>
          <SentryRoute path={`${path}/payment-verification/cash-plan/:id`}>
            <CashPlanVerificationDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/payment-verification/payment-plan/:id`}>
            <PaymentPlanVerificationDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/csh-payment-verification/:id`}>
            <CashPlanVerificationRedirectPage />
          </SentryRoute>
          <SentryRoute path={`${path}/payment-module/new-plan`}>
            <CreatePaymentPlanPage />
          </SentryRoute>
          <SentryRoute exact path={`${path}/payment-module`}>
            <PaymentModulePage />
          </SentryRoute>
          <SentryRoute
            path={`${path}/payment-module/followup-payment-plans/:id/edit`}
          >
            <EditFollowUpPaymentPlanPage />
          </SentryRoute>
          <SentryRoute
            path={`${path}/payment-module/followup-payment-plans/:id/setup-fsp/create`}
          >
            <SetFollowUpUpFspPage />
          </SentryRoute>
          <SentryRoute
            path={`${path}/payment-module/followup-payment-plans/:id/setup-fsp/edit`}
          >
            <EditFollowUpSetUpFspPage />
          </SentryRoute>
          <SentryRoute
            path={`${path}/payment-module/payment-plans/:id/setup-fsp/create`}
          >
            <SetUpFspPage />
          </SentryRoute>
          <SentryRoute
            path={`${path}/payment-module/payment-plans/:id/setup-fsp/edit`}
          >
            <EditSetUpFspPage />
          </SentryRoute>
          <SentryRoute path={`${path}/payment-module/payment-plans/:id/edit`}>
            <EditPaymentPlanPage />
          </SentryRoute>
          <SentryRoute path={`${path}/payment-module/payments/:id`}>
            <PaymentDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/payment-module/payment-plans/:id`}>
            <PaymentPlanDetailsPage />
          </SentryRoute>
          <SentryRoute
            path={`${path}/payment-module/followup-payment-plans/:id`}
          >
            <FollowUpPaymentPlanDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/grievance/new-ticket`}>
            <CreateGrievancePage />
          </SentryRoute>
          <SentryRoute
            path={`${path}/grievance/edit-ticket/user-generated/:id`}
          >
            <EditGrievancePage key='user' />
          </SentryRoute>
          <SentryRoute
            path={`${path}/grievance/edit-ticket/system-generated/:id`}
          >
            <EditGrievancePage key='system' />
          </SentryRoute>
          <SentryRoute path={`${path}/grievance/tickets/user-generated/:id`}>
            <GrievancesDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/grievance/tickets/system-generated/:id`}>
            <GrievancesDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/grievance/rdi/:id`}>
            <GrievancesTablePage key='rdi' />
          </SentryRoute>
          <SentryRoute
            path={`${path}/grievance/payment-verification/:cashPlanId`}
          >
            <GrievancesTablePage key='verificationId' />
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

          <SentryRoute path={`${path}/accountability/feedback/create`}>
            <CreateFeedbackPage />
          </SentryRoute>
          <SentryRoute path={`${path}/accountability/feedback/edit-ticket/:id`}>
            <EditFeedbackPage />
          </SentryRoute>
          <SentryRoute path={`${path}/accountability/feedback/:id`}>
            <FeedbackDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/accountability/feedback`}>
            <FeedbackPage />
          </SentryRoute>
          {/* TODO: uncomment when ready for deployment
          <SentryRoute path={`${path}/accountability/surveys/create`}>
            <CreateSurveyPage />
          </SentryRoute>
          <SentryRoute path={`${path}/accountability/surveys/:id`}>
            <SurveyDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/accountability/surveys`}>
            <SurveysPage />
          </SentryRoute>
             <SentryRoute path={`${path}/accountability/communication/create`}>
            <CreateCommunicationPage />
          </SentryRoute>
          <SentryRoute path={`${path}/accountability/communication/:id`}>
            <CommunicationDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/accountability/communication`}>
            <CommunicationPage />
          </SentryRoute>
          */}
          <SentryRoute path={`${path}/population/household`}>
            <PopulationHouseholdPage />
          </SentryRoute>
          <SentryRoute path={`${path}/population/individuals`}>
            <PopulationIndividualsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/details/:id`}>
            <ProgramDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/payment-records/:id`}>
            <PaymentRecordDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/list`}>
            <ProgramsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/registration-data-import/household/:id`}>
            <RegistrationHouseholdDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/registration-data-import/individual/:id`}>
            <RegistrationIndividualDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/registration-data-import/:id`}>
            <RegistrationDataImportDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/registration-data-import`}>
            <RegistrationDataImportPage />
          </SentryRoute>
          <SentryRoute path={`${path}/reporting/:id`}>
            <ReportingDetailsPage />
          </SentryRoute>
          <SentryRoute path={`${path}/reporting`}>
            <ReportingPage />
          </SentryRoute>
          <SentryRoute path={`${path}/users-list`}>
            <UsersPage />
          </SentryRoute>
          <SentryRoute path={`${path}/activity-log`}>
            <ActivityLogPage />
          </SentryRoute>
          <SentryRoute label='/ - Dashboard' path={`${path}/`}>
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
};
