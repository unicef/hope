import React from 'react';
import { RelayEnvironmentProvider } from 'relay-hooks';
import { environment } from './relay/enviroment';
import { ThemeProvider } from '@material-ui/core';
import {
  Route,
  Switch,
  BrowserRouter as Router,
  Redirect,
} from 'react-router-dom';
import { theme } from './theme';
import { HomeRouter } from './containers/HomeRouter';
import { LoginPage } from './containers/pages/LoginPage';

export const App: React.FC = () => {
  const authenticated = true;
  return (
    <RelayEnvironmentProvider environment={environment}>
      <ThemeProvider theme={theme}>
        <Router>
          <Switch>
            <Route path='/login'>
              <LoginPage />
            </Route>
            <Route path='/'>
              {!authenticated ? <Redirect to='/login' /> : <HomeRouter />}
            </Route>
          </Switch>
        </Router>
      </ThemeProvider>
    </RelayEnvironmentProvider>
  );
};
