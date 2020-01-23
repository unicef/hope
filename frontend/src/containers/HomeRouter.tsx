import React, { useEffect } from 'react';
import styled from 'styled-components';
import { makeStyles } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { Route, Switch, useLocation } from 'react-router-dom';
import { MiśTheme } from '../theme';
import { Drawer } from '../components/Drawer/Drawer';
import { AppBar } from '../components/AppBar';
import { DashboardPage } from './pages/DashboardPage';
import { ProgramsPage } from './pages/ProgramsPage';
import { ProgramDetailsPage } from './pages/ProgramDetailsPage';
import { isAuthenticated } from '../utils/utils';
import { LOGIN_URL } from '../config';

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

  useEffect(() => {
    if (!authenticated) {
      window.location.replace(LOGIN_URL);
    }
  }, [authenticated]);
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
    return null;
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
          <Route path='/programs/:id'>
            <ProgramDetailsPage />
          </Route>
          <Route path='/programs'>
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
