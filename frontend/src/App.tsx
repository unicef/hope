import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { AutoLogout } from './components/core/AutoLogout';
import { DefaultRoute } from './containers/DefaultRoute';
import { HomeRouter } from './containers/HomeRouter';
import { LoginPage } from './containers/pages/core/LoginPage';
import { ProfilePage } from './containers/pages/core/ProfilePage';
import { Providers } from './providers';
import { SentryRoute } from './components/core/SentryRoute';
import { MaintenancePage } from './containers/pages/maintenance/MaintenancePage';
import { SanctionList } from './containers/pages/core/SanctionList';
import { ProtectedRoute } from './components/core/ProtectedRoute';
import { PageNotFound } from './containers/pages/404/PageNotFound';
import { SomethingWentWrong } from './containers/pages/SomethingWentWrong/SomethingWentWrong';

export const App: React.FC = () => {
  return (
    <Providers>
      <AutoLogout />
      <Router>
        <Switch>
          <SentryRoute path='/login'>
            <LoginPage />
          </SentryRoute>
          <SentryRoute path='/maintenance'>
            <MaintenancePage />
          </SentryRoute>
          <SentryRoute path='/404'>
            <PageNotFound />
          </SentryRoute>
          <SentryRoute path='/error'>
            <SomethingWentWrong />
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
          <ProtectedRoute
            path='/sanction-list'
            component={SanctionList}
            location={window.location}
          />
          <SentryRoute path='/accounts/profile/'>
            <ProfilePage />
          </SentryRoute>
          <ProtectedRoute
            path='/sanction-list'
            component={SanctionList}
            location={window.location}
          />
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
