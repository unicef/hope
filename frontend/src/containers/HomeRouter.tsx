import React from 'react';
import styled from 'styled-components';
import { makeStyles } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { Redirect, Route, Switch, useLocation } from 'react-router-dom';
import { MiśTheme } from '../theme';
import { Drawer } from '../components/Drawer/Drawer';
import { AppBar } from '../components/AppBar';
import { isAuthenticated } from '../utils/utils';
import { DashboardPage } from './pages/DashboardPage';
import { ProgramsPage } from './pages/ProgramsPage';
import { ProgramDetailsPage } from './pages/ProgramDetailsPage';
import { PaymentRecordDetailsPage } from './pages/PaymentRecordDetailsPage';

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
          <Route path='/:businessArea/programs/:id'>
            <ProgramDetailsPage />
          </Route>
          <Route path='/:businessArea/payment_records/:id'>
            <PaymentRecordDetailsPage />
          </Route>
          <Route path='/:businessArea/payment_records/:id'>
            <PaymentRecordDetailsPage />
          </Route>
          <Route path='/:businessArea/programs'>
            <ProgramsPage />
          </Route>
          <Route path='/'>
            <DashboardPage />
          </Route>
        </Switch>
      </MainContent>
    </Root>
  );
}
