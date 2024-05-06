import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { PopulationHouseholdDetailsPage } from '../pages/population/PopulationHouseholdDetailsPage';
import { PopulationHouseholdPage } from '../pages/population/PopulationHouseholdPage';
import { PopulationIndividualsDetailsPage } from '../pages/population/PopulationIndividualsDetailsPage';
import { PopulationIndividualsPage } from '../pages/population/PopulationIndividualsPage';
import { PeoplePage } from '@containers/pages/people/PeoplePage';
import { PeopleDetailsPage } from '@containers/pages/people/PeopleDetailsPage';

export const PopulationRoutes = (): React.ReactElement => {
  const populationRoutes = [
    {
      path: 'population/household/:id',
      element: <PopulationHouseholdDetailsPage />,
    },
    {
      path: 'population/individuals/:id',
      element: <PopulationIndividualsDetailsPage />,
    },
    {
      path: 'population/people/:id',
      element: <PeopleDetailsPage />,
    },
    {
      path: 'population/household',
      element: <PopulationHouseholdPage />,
    },
    {
      path: 'population/individuals',
      element: <PopulationIndividualsPage />,
    },
    {
      path: 'population/people',
      element: <PeoplePage />,
    },
  ];

  return useRoutes(populationRoutes);
};
