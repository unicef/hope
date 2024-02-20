import * as React from 'react';
import { Route, useLocation, useRoutes } from 'react-router-dom';
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
        <Route
          path={`${path}/registration-data-import/household/:id`}
          element={<RegistrationHouseholdDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/registration-data-import/individual/:id`,
      element: (
        <Route
          path={`${path}/registration-data-import/individual/:id`}
          element={<RegistrationIndividualDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/registration-data-import/:id`,
      element: (
        <Route
          path={`${path}/registration-data-import/:id`}
          element={<RegistrationDataImportDetailsPage />}
        />
      ),
    },
    {
      path: `${path}/registration-data-import`,
      element: (
        <Route
          path={`${path}/registration-data-import`}
          element={<RegistrationDataImportPage />}
        />
      ),
    },
  ];

  return useRoutes(registrationRoutes);
};
