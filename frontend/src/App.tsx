import React from 'react';
import { Route, BrowserRouter as Router, Switch } from 'react-router-dom';
import { AutoLogout } from './components/core/AutoLogout';
import { SentryRoute } from './components/core/SentryRoute';
import { DefaultRoute } from './containers/DefaultRoute';
import { LoginPage } from './containers/pages/core/LoginPage';
import { ProfilePage } from './containers/pages/core/ProfilePage';
import { MaintenancePage } from './containers/pages/maintenance/MaintenancePage';
import { AllProgramsRoutesSwitch } from './containers/routers/AllProgramsRoutesSwitch';
import { BaseHomeRouter } from './containers/routers/BaseHomeRouter';
import { SelectedProgramRoutesSwitch } from './containers/routers/SelectedProgramRoutesSwitch';
import { Providers } from './providers';
import { SanctionList } from './containers/pages/core/SanctionList';
import { ProtectedRoute } from './components/core/ProtectedRoute';
import { PageNotFound } from './containers/pages/404/PageNotFound';
import { AccessDenied } from './containers/pages/accessDenied/AccessDenied';
import {SomethingWentWrong} from "./containers/pages/SomethingWentWrong/SomethingWentWrong";

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
          <SentryRoute path='/access-denied'>
            <AccessDenied />
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
          <Route path='/:businessArea/programs/all'>
            <BaseHomeRouter>
              <AllProgramsRoutesSwitch />
            </BaseHomeRouter>
          </Route>
          <Route path='/:businessArea/programs/:programId'>
            <BaseHomeRouter>
              <SelectedProgramRoutesSwitch />
            </BaseHomeRouter>
            <ProtectedRoute
              path='/sanction-list'
              component={SanctionList}
              location={window.location}
            />
          </Route>
          <Route path='/'>
            <DefaultRoute />
          </Route>
        </Switch>
      </Router>
    </Providers>
  );
};
