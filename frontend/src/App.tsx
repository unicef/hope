import React from 'react';
import { Route, BrowserRouter as Router, Switch } from 'react-router-dom';
import { AutoLogout } from './components/core/AutoLogout';
import { SentryRoute } from './components/core/SentryRoute';
import { DefaultRoute } from './containers/DefaultRoute';
import { LoginPage } from './containers/pages/core/LoginPage';
import { ProfilePage } from './containers/pages/core/ProfilePage';
import { AllProgramsRoutesSwitch } from './containers/routers/AllProgramsRoutesSwitch';
import { BaseHomeRouter } from './containers/routers/BaseHomeRouter';
import { SelectedProgramRoutesSwitch } from './containers/routers/SelectedProgramRoutesSwitch';
import { Providers } from './providers';

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
          <Route path='/:businessArea/programs/all'>
            <BaseHomeRouter>
              <AllProgramsRoutesSwitch />
            </BaseHomeRouter>
          </Route>
          <Route path='/:businessArea/programs/:programId'>
            <BaseHomeRouter>
              <SelectedProgramRoutesSwitch />
            </BaseHomeRouter>
          </Route>
          <Route path='/'>
            <DefaultRoute />
          </Route>
        </Switch>
      </Router>
    </Providers>
  );
};
