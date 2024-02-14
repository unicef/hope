import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
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
import { SomethingWentWrong } from './containers/pages/somethingWentWrong/SomethingWentWrong';

export const App: React.FC = () => (
  <Providers>
    <AutoLogout />
    <Router>
      <Routes>
        <SentryRoute path="/login" element={<LoginPage />} />
        <SentryRoute path="/maintenance" element={<MaintenancePage />} />
        <SentryRoute path="/404" element={<PageNotFound />} />
        <SentryRoute path="/error" element={<SomethingWentWrong />} />
        <SentryRoute path="/access-denied" element={<AccessDenied />} />
        <SentryRoute
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
        <ProtectedRoute path="/sanction-list" element={<SanctionList />} />
        <SentryRoute path="/accounts/profile/" element={<ProfilePage />} />
        <Route
          path="/:businessArea/programs/all"
          element={
            <BaseHomeRouter>
              <AllProgramsRoutesSwitch />
            </BaseHomeRouter>
          }
        />
        <Route
          path="/:businessArea/programs/:programId"
          element={
            <BaseHomeRouter>
              <SelectedProgramRoutesSwitch />
            </BaseHomeRouter>
          }
        />
        <Route path="/" element={<DefaultRoute />} />
      </Routes>
    </Router>
  </Providers>
);
