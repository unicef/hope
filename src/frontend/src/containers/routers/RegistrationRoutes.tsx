import { useRoutes } from 'react-router-dom';
import { RegistrationDataImportDetailsPage } from '../pages/rdi/RegistrationDataImportDetailsPage';
import { RegistrationDataImportPage } from '../pages/rdi/RegistrationDataImportPage';
import { useProgramContext } from '../../programContext';
import { PeopleRegistrationDataImportPage } from '@containers/pages/rdi/people/PeopleRegistrationDataImportPage';
import { PeopleRegistrationDetailsPage } from '@containers/pages/rdi/people/PeopleRegistrationDetailsPage';
import { PeopleRegistrationDataImportDetailsPage } from '@containers/pages/rdi/people/PeopleRegistrationDataImportDetailsPage';
import { ReactElement } from 'react';

export const RegistrationRoutes = (): ReactElement => {
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
