import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { ProgramDetailsPage } from '../pages/program/ProgramDetailsPage';
import { ProgramsPage } from '../pages/program/ProgramsPage';
import { CreateProgramPage } from '../pages/program/CreateProgramPage';
import { EditProgramPage } from '../pages/program/EditProgramPage';
import { DuplicateProgramPage } from '../pages/program/DuplicateProgramPage';

export const ProgramRoutes = (): React.ReactElement => {
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
