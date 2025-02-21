import { useRoutes } from 'react-router-dom';
import { ReactElement } from 'react';
import CreateProgramPage from '@containers/pages/program/CreateProgramPage';
import DuplicateProgramPage from '@containers/pages/program/DuplicateProgramPage';
import EditProgramPage from '@containers/pages/program/EditProgramPage';
import ProgramDetailsPage from '@containers/pages/program/ProgramDetailsPage';
import ProgramsPage from '@containers/pages/program/ProgramsPage';

export const ProgramRoutes = (): ReactElement => {
  const programRoutes = [
    {
      path: 'list',
      element: <ProgramsPage />,
    },
    {
      path: 'create',
      element: <CreateProgramPage />,
    },
    {
      path: 'edit/:id',
      element: <EditProgramPage />,
    },
    {
      path: 'duplicate/:id',
      element: <DuplicateProgramPage />,
    },
    {
      path: 'details/:id',
      element: <ProgramDetailsPage />,
    },
  ];

  return useRoutes(programRoutes);
};
