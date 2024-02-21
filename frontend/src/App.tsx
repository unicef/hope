import { DefaultRoute } from '@containers/DefaultRoute';
import { PageNotFound } from '@containers/pages/404/PageNotFound';
import { AccessDenied } from '@containers/pages/accessDenied/AccessDenied';
import { LoginPage } from '@containers/pages/core/LoginPage';
import { ProfilePage } from '@containers/pages/core/ProfilePage';
import { SanctionList } from '@containers/pages/core/SanctionList';
import { MaintenancePage } from '@containers/pages/maintenance/MaintenancePage';
import { SomethingWentWrong } from '@containers/pages/somethingWentWrong/SomethingWentWrong';
import { AllProgramsRoutesSwitch } from '@containers/routers/AllProgramsRoutesSwitch';
import { BaseHomeRouter } from '@containers/routers/BaseHomeRouter';
import { SelectedProgramRoutesSwitch } from '@containers/routers/SelectedProgramRoutesSwitch';
import { AutoLogout } from '@core/AutoLogout';

import React from 'react';
import {
  createBrowserRouter,
  Route,
  RouterProvider,
  Routes,
} from 'react-router-dom';
import { Providers } from './providers';

const Root: React.FC = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/maintenance" element={<MaintenancePage />} />
    <Route path="/404" element={<PageNotFound />} />
    <Route path="/error" element={<SomethingWentWrong />} />
    <Route path="/access-denied" element={<AccessDenied />} />
    <Route
      path="/sentry-check"
      element={
        <button
          type="button"
          onClick={() => {
            throw new Error('Am I working?');
          }}
        >
          Throw new error
        </button>
      }
    />
    <Route path="/sanction-list" element={<SanctionList />} />
    <Route path="/accounts/profile/" element={<ProfilePage />} />
    <Route element={<BaseHomeRouter />}>
      <Route
        path="/:businessArea/programs/all/*"
        element={<AllProgramsRoutesSwitch />}
      />
      <Route
        path="/:businessArea/programs/:programId/*"
        element={<SelectedProgramRoutesSwitch />}
      />
    </Route>
    <Route path="/" element={<DefaultRoute />} />
  </Routes>
);

const router = createBrowserRouter([{ path: '*', Component: Root }]);

export const App: React.FC = () => (
  <Providers>
    <AutoLogout />
    <RouterProvider router={router} />
  </Providers>
);
