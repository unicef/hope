import { DefaultRoute } from '@containers/DefaultRoute';
import { PageNotFound } from '@containers/pages/404/PageNotFound';
import { AccessDenied } from '@containers/pages/accessDenied/AccessDenied';
import { LoginPage } from '@containers/pages/core/LoginPage';
import { ProfilePage } from '@containers/pages/core/ProfilePage';
import { MaintenancePage } from '@containers/pages/maintenance/MaintenancePage';
import { SomethingWentWrong } from '@containers/pages/somethingWentWrong/SomethingWentWrong';
import { AllProgramsRoutesSwitch } from '@containers/routers/AllProgramsRoutesSwitch';
import { BaseHomeRouter } from '@containers/routers/BaseHomeRouter';
import { SelectedProgramRoutesSwitch } from '@containers/routers/SelectedProgramRoutesSwitch';
import { AutoLogout } from '@core/AutoLogout';
import React, { FC, useEffect } from 'react';
import {
  createBrowserRouter,
  Route,
  RouterProvider,
  Routes,
  useNavigate,
  useParams,
} from 'react-router-dom';
import { Providers } from './providers';
import * as Sentry from '@sentry/react';

const RedirectToPrograms: FC = () => {
  const navigate = useNavigate();
  const { businessArea } = useParams();

  useEffect(() => {
    navigate(`/${businessArea}/programs/all/list`);
  }, [navigate, businessArea]);

  return null;
};

const Root: FC = () => (
  <Routes>
    <Route path="/login/*" element={<LoginPage />} />
    <Route path="/maintenance/*" element={<MaintenancePage />} />
    <Route path="/404/*" element={<PageNotFound />} />
    <Route path="/access-denied/*" element={<AccessDenied />} />
    <Route path="/error/*" element={<SomethingWentWrong />} />
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
    <Route path="/:businessArea" element={<RedirectToPrograms />} />
  </Routes>
);

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouter(createBrowserRouter);
const router = sentryCreateBrowserRouter([{ path: '*', Component: Root }]);

export const App: FC = () => (
  <Providers>
    <AutoLogout />
    <RouterProvider router={router} />
  </Providers>
);
