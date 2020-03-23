import React from 'react';
import styled from 'styled-components';
import { makeStyles, Snackbar, SnackbarContent } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { Redirect, Route, Switch, useLocation } from 'react-router-dom';
import { MiśTheme } from '../theme';
import { Drawer } from '../components/Drawer/Drawer';
import { AppBar } from '../components/AppBar';
import { isAuthenticated } from '../utils/utils';
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
import { RegistrationDataImport } from './registration/import/RegistrationDataImport';
import { RegistrationDataImportDetailsPage } from './registration/details/RegistrationDataImportDetailsPage';
import { RegistrationHouseholdDetailsPage } from './registration/details/households/RegistrationHouseholdDetailsPage';
import { RegistrationIndividualDetailsPage } from './registration/details/individual/RegistrationIndividualDetailsPage';
import { useSnackbar } from '../hooks/useSnackBar';

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
  const authenticated = isAuthenticated();
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

  if (!authenticated) {
    return <Redirect to='/login' />;
  }
  return (
    <Root>
      <CssBaseline />
      <AppBar open={open} handleDrawerOpen={handleDrawerOpen} />
      <Drawer
        open={open}
        handleDrawerClose={handleDrawerClose}
        currentLocation={location.pathname}
      />
      <MainContent>
        <div className={classes.appBarSpacer} />
        <Switch>
          <Route path='/:businessArea/population/household/:id'>
            <PopulationHouseholdDetailsPage />
          </Route>
          <Route path='/:businessArea/population/individuals/:id'>
            <PopulationIndividualsDetailsPage />
          </Route>
          <Route path='/:businessArea/cashplans/:id'>
            <CashPlanDetailsPage />
          </Route>
          <Route exact path='/:businessArea/target-population'>
            <TargetPopulationPage />
          </Route>
          <Route path='/:businessArea/target-population/create'>
            <CreateTargetPopulation />
          </Route>
          <Route path='/:businessArea/target-population/:id'>
            <TargetPopulationDetailsPage />
          </Route>
          <Route path='/:businessArea/population/household'>
            <PopulationHouseholdPage />
          </Route>
          <Route path='/:businessArea/population/individuals'>
            <PopulationIndividualsPage />
          </Route>
          <Route path='/:businessArea/programs/:id'>
            <ProgramDetailsPage />
          </Route>
          <Route path='/:businessArea/payment_records/:id'>
            <PaymentRecordDetailsPage />
          </Route>
          <Route path='/:businessArea/programs'>
            <ProgramsPage />
          </Route>
          <Route path='/:businessArea/registration-data-import/household/:id'>
            <RegistrationHouseholdDetailsPage />
          </Route>
          <Route path='/:businessArea/registration-data-import/individual/:id'>
            <RegistrationIndividualDetailsPage />
          </Route>
          <Route path='/:businessArea/registration-data-import/:id'>
            <RegistrationDataImportDetailsPage />
          </Route>
          <Route path='/:businessArea/registration-data-import'>
            <RegistrationDataImportPage />
          </Route>

          <Route path='/'>
            <DashboardPage />
          </Route>
        </Switch>
      </MainContent>
      {snackBar.show && (
        <Snackbar
          open={snackBar.show}
          autoHideDuration={5000}
          onClose={() => snackBar.setShow(false)}
        >
          <SnackbarContent message={snackBar.message} />
        </Snackbar>
      )}
    </Root>
  );
}
