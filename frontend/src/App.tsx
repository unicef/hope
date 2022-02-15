import * as Sentry from '@sentry/react';
import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { AutoLogout } from './components/core/AutoLogout';
import { ProtectedRoute } from './components/core/ProtectedRoute';
import { DefaultRoute } from './containers/DefaultRoute';
import { HomeRouter } from './containers/HomeRouter';
import { LoginPage } from './containers/pages/core/LoginPage';
import { ProfilePage } from './containers/pages/core/ProfilePage';
import { SanctionList } from './containers/pages/core/SanctionList';
import { Providers } from './providers';

export const App: React.FC = () => {
  return (
    <Providers>
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
              <button
                type='button'
                onClick={() => {
                  throw new Error('Am I working?');
                }}
              >
                Throw new error
              </button>
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
    </Providers>
  );
};
