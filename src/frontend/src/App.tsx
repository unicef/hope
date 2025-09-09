import { DefaultRoute } from '@containers/DefaultRoute';
import { PageNotFound } from '@containers/pages/404/PageNotFound';
import { AccessDenied } from '@containers/pages/accessDenied/AccessDenied';
import { LoginPage } from '@containers/pages/core/LoginPage';
import { MaintenancePage } from '@containers/pages/maintenance/MaintenancePage';
import { SomethingWentWrong } from '@containers/pages/somethingWentWrong/SomethingWentWrong';
import { AllProgramsRoutesSwitch } from '@containers/routers/AllProgramsRoutesSwitch';
import { BaseHomeRouter } from '@containers/routers/BaseHomeRouter';
import { SelectedProgramRoutesSwitch } from '@containers/routers/SelectedProgramRoutesSwitch';
import { AutoLogout } from '@core/AutoLogout';
import * as Sentry from '@sentry/react';
import { FC, useEffect } from 'react';
import {
  createBrowserRouter,
  Route,
  RouterProvider,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom';
import { Providers } from './providers';

const GlobalDashboardRedirect: FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  useEffect(() => {
    const path = location.pathname;
    if (
      path.startsWith('/global') &&
      path !== '/global/programs/all/country-dashboard'
    ) {
      navigate('/global/programs/all/country-dashboard', { replace: true });
    }
  }, [location, navigate]);
  return null;
};

const RedirectToPrograms: FC = () => {
  const navigate = useNavigate();
  const { businessArea } = useParams();

  useEffect(() => {
    navigate(`/${businessArea}/programs/all/list`);
  }, [navigate, businessArea]);

  return null;
};

const Root: FC = () => (
  <>
    <GlobalDashboardRedirect />
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
  </>
);

const sentryCreateBrowserRouter =
  Sentry.wrapCreateBrowserRouter(createBrowserRouter);
const router = sentryCreateBrowserRouter([
  {
    path: '*',
    Component: Root,
    future: {
      v7_fetcherPersist: true,
      v7_relativeSplatPath: true,
    },
  },
]);

export const App: FC = () => (
  <Providers>
    <AutoLogout />
    <RouterProvider router={router} />
  </Providers>
);
