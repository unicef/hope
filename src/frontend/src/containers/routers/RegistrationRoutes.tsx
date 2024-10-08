import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { RegistrationDataImportDetailsPage } from '../pages/rdi/RegistrationDataImportDetailsPage';
import { RegistrationDataImportPage } from '../pages/rdi/RegistrationDataImportPage';
import { RegistrationHouseholdDetailsPage } from '../pages/rdi/RegistrationHouseholdDetailsPage';
import { RegistrationIndividualDetailsPage } from '../pages/rdi/RegistrationIndividualDetailsPage';
import { useProgramContext } from '../../programContext';
import { PeopleRegistrationDataImportPage } from '@containers/pages/rdi/people/PeopleRegistrationDataImportPage';
import { PeopleRegistrationDetailsPage } from '@containers/pages/rdi/people/PeopleRegistrationDetailsPage';
import { PeopleRegistrationDataImportDetailsPage } from '@containers/pages/rdi/people/PeopleRegistrationDataImportDetailsPage';

export const RegistrationRoutes = (): React.ReactElement => {
  const { isSocialDctType } = useProgramContext();

  let children = [];

  if (isSocialDctType) {
    children = [
      {
        path: '',
        element: <PeopleRegistrationDataImportPage />,
      },
      {
        path: 'people/:id',
        element: <PeopleRegistrationDetailsPage />,
      },
      {
        path: ':id',
        element: <PeopleRegistrationDataImportDetailsPage />,
      },
    ];
  } else {
    children = [
      {
        path: '',
        element: <RegistrationDataImportPage />,
      },
      {
        path: 'household/:id',
        element: <RegistrationHouseholdDetailsPage />,
      },
      {
        path: 'individual/:id',
        element: <RegistrationIndividualDetailsPage />,
      },
      {
        path: ':id',
        element: <RegistrationDataImportDetailsPage />,
      },
    ];
  }

  const registrationRoutes = [
    {
      path: 'registration-data-import',
      children,
    },
  ];

  return useRoutes(registrationRoutes);
};
