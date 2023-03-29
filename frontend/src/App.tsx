import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { AutoLogout } from './components/core/AutoLogout';
import { DefaultRoute } from './containers/DefaultRoute';
import { HomeRouter } from './containers/HomeRouter';
import { LoginPage } from './containers/pages/core/LoginPage';
import { ProfilePage } from './containers/pages/core/ProfilePage';
import { Providers } from './providers';
import { SentryRoute } from './components/core/SentryRoute';

export const App: React.FC = () => {
  return (
    <Providers>
      <AutoLogout />
      <Router>
        <Switch>
          <SentryRoute path='/login'>
            <LoginPage />
          </SentryRoute>
          <SentryRoute path='/sentry-check'>
            <button
              type='button'
              onClick={() => {
                throw new Error('Am I working?');
              }}
            >
              Throw new error
            </button>
          </SentryRoute>
          <SentryRoute path='/accounts/profile/'>
            <ProfilePage />
          </SentryRoute>
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
