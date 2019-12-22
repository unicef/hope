import React from 'react';
import clsx from 'clsx';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import { makeStyles } from '@material-ui/core';
import { Drawer } from '../components/Drawer/Drawer';
import { MiśTheme } from '../theme';
import { AppBar } from '../components/AppBar';
import { Route, Switch, useLocation } from 'react-router-dom';
import { DashboardPage } from './DashboardPage';
import { ProgramsPage } from './ProgramsPage';

const useStyles = makeStyles((theme: MiśTheme) => ({
  root: {
    display: 'flex',
  },
  appBarSpacer: theme.mixins.toolbar,
  content: {
    flexGrow: 1,
    height: '100vh',
    overflow: 'auto',
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column',
  },
  fixedHeight: {
    height: 240,
  },
}));

export function HomeRouter(): React.ReactElement {
  const isAuthenticated = false;
  const classes = useStyles({});
  const [open, setOpen] = React.useState(true);
  const location = useLocation();
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  console.log('location', location.pathname);
  const handleDrawerClose = () => {
    setOpen(false);
  };
  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar open={open} handleDrawerOpen={handleDrawerOpen} />
      <Drawer
        open={open}
        handleDrawerClose={handleDrawerClose}
        currentLocation={location.pathname}
      />
      <main className={classes.content}>
        <div className={classes.appBarSpacer} />
        <Switch>
          <Route path='/programs'>
            <ProgramsPage />
          </Route>
          <Route path='/'>
            <DashboardPage />
          </Route>
        </Switch>
      </main>
    </div>
  );
}
