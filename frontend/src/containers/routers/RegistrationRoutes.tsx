import * as React from 'react';
import { useRoutes, useLocation } from 'react-router-dom';
import { SentryRoute } from '@components/core/SentryRoute';
import { RegistrationDataImportDetailsPage } from '../pages/rdi/RegistrationDataImportDetailsPage';
import { RegistrationDataImportPage } from '../pages/rdi/RegistrationDataImportPage';
import { RegistrationHouseholdDetailsPage } from '../pages/rdi/RegistrationHouseholdDetailsPage';
import { RegistrationIndividualDetailsPage } from '../pages/rdi/RegistrationIndividualDetailsPage';

export const RegistrationRoutes = (): React.ReactElement => {
  const location = useLocation();
  const path = location.pathname;

  const registrationRoutes = [
    {
      path: `${path}/registration-data-import/household/:id`,
      element: (
        <SentryRoute
          path={`${path}/registration-data-import/household/:id`}
          element={<RegistrationHouseholdDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/registration-data-import/individual/:id`,
      element: (
        <SentryRoute
          path={`${path}/registration-data-import/individual/:id`}
          element={<RegistrationIndividualDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/registration-data-import/:id`,
      element: (
        <SentryRoute
          path={`${path}/registration-data-import/:id`}
          element={<RegistrationDataImportDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/registration-data-import`,
      element: (
        <SentryRoute
          path={`${path}/registration-data-import`}
          element={<RegistrationDataImportPage />}
        />
      ),
    },
  ];

  const routes = useRoutes(registrationRoutes);

  return routes;
};
