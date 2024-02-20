import * as React from 'react';
import { useLocation, useRoutes } from 'react-router-dom';
import { ProgramDetailsPage } from '../pages/program/ProgramDetailsPage';
import { ProgramsPage } from '../pages/program/ProgramsPage';
import { CreateProgramPage } from '../pages/program/CreateProgramPage';
import { EditProgramPage } from '../pages/program/EditProgramPage';
import { DuplicateProgramPage } from '../pages/program/DuplicateProgramPage';

export const ProgramRoutes = (): React.ReactElement => {
  const location = useLocation();
  const path = location.pathname;

  const programRoutes = [
    {
      path: `${path}/list`,
      element: <ProgramsPage />,
    },
    {
      path: `${path}/create`,
      element: <CreateProgramPage />,
    },
    {
      path: `${path}/edit/:id`,
      element: <EditProgramPage />,
    },
    {
      path: `${path}/duplicate/:id`,
      element: <DuplicateProgramPage />,
    },
    {
      path: `${path}/details/:id`,
      element: <ProgramDetailsPage />,
    },
  ];

  return useRoutes(programRoutes);
};
