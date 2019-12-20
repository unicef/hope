import React from 'react';
import clsx from 'clsx';
import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import {makeStyles} from '@material-ui/core';
import {Drawer} from '../components/Drawer/Drawer';
import {MiśTheme} from '../theme';
import {AppBar} from "../components/AppBar";
import {LoginPage} from "./LoginPage";
import { Route, Switch, BrowserRouter as Router } from 'react-router-dom';
import {DashboardPage} from "./DashboardPage";
import {ProgramsPage} from "./ProgramsPage";


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
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };
  const fixedHeightPaper = clsx(classes.paper, classes.fixedHeight);
  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar open={open} handleDrawerOpen={handleDrawerOpen}/>
      <Drawer open={open} handleDrawerClose={handleDrawerClose} />
      <main className={classes.content}>
        <div className={classes.appBarSpacer} />
        <Container maxWidth='lg' className={classes.container}>
          <Switch>
            <Route path='/'>
              <DashboardPage />
            </Route>
            <Route path='/programs'>
              <ProgramsPage />
            </Route>
          </Switch>
        </Container>
      </main>
    </div>
  );
}
