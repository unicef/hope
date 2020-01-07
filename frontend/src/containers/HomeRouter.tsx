import React from 'react';
import CssBaseline from '@material-ui/core/CssBaseline';
import { Drawer } from '../components/Drawer/Drawer';
import { AppBar } from '../components/AppBar';
import { Route, Switch, useLocation } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { ProgramsPage } from './pages/ProgramsPage';
import { ProgramDetailsPage } from './pages/ProgramDetailsPage';
import styled from 'styled-components';
import styledJSS from 'styled-jss';


const Root = styled.div`
  display: flex;
`;
const MainContent = styled.div`
  flex-grow: 1;
  height: 100vh;
  overflow: auto;
`;
const AppBarSpacer = styledJSS('div')(({ theme }) => ({
  ...theme.mixins.toolbar,
}));

export function HomeRouter(): React.ReactElement {
  const [open, setOpen] = React.useState(true);
  const location = useLocation();
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
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
      />
      <MainContent>
        <AppBarSpacer/>
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
