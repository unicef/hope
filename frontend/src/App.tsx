import React from 'react';
import {ThemeProvider} from '@material-ui/core';
import {ThemeProvider as StyledThemeProvider} from 'styled-components';
import {BrowserRouter as Router, Route, Switch} from 'react-router-dom';
import CssBaseline from '@material-ui/core/CssBaseline';
import {MuiPickersUtilsProvider} from '@material-ui/pickers';
import moment from 'moment';
import MomentUtils from '@date-io/moment';
import {ApolloProvider} from '@apollo/react-hooks';
import * as Sentry from '@sentry/react';
import {theme} from './theme';
import {HomeRouter} from './containers/HomeRouter';
import {ProfilePage} from './containers/pages/ProfilePage';
import {client} from './apollo/client';
import {LoginPage} from './containers/pages/LoginPage';
import {DefaultRoute} from './containers/DefaultRoute';
import {SanctionList} from './containers/pages/SanctionList';
import {ProtectedRoute} from './components/ProtectedRoute';
import {AutoLogout} from './components/AutoLogout';

export const App: React.FC = () => {
  return (
    <ApolloProvider client={client}>
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <MuiPickersUtilsProvider libInstance={moment} utils={MomentUtils}>
            <CssBaseline />
            <AutoLogout />
            <Router>
              <Switch>
                <Route path='/login'>
                  <Sentry.ErrorBoundary
                    beforeCapture={(scope) => {
                      scope.setTag('location', '/login');
                    }}
                  >
                    <LoginPage />
                  </Sentry.ErrorBoundary>
                </Route>
                <Route path='/sentry-check'>
                  <Sentry.ErrorBoundary
                    beforeCapture={(scope) => {
                      scope.setTag('location', '/sentry-check/');
                    }}
                  >
                    <button type="button" onClick={() => { throw new Error('Am I working?')}}>Throw new error</button>
                  </Sentry.ErrorBoundary>
                </Route>
                <ProtectedRoute
                  path='/sanction-list'
                  component={SanctionList}
                  location={window.location}
                />
                <Route path='/accounts/profile/'>
                  <Sentry.ErrorBoundary
                    beforeCapture={(scope) => {
                      scope.setTag('location', '/accounts/profile/');
                    }}
                  >
                    <ProfilePage />
                  </Sentry.ErrorBoundary>
                </Route>
                <Route path='/:businessArea/'>
                  <HomeRouter />
                </Route>
                <Route path='/'>
                  <DefaultRoute />
                </Route>
              </Switch>
            </Router>
          </MuiPickersUtilsProvider>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
};
