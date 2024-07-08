import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { PopulationHouseholdDetailsPage } from '../pages/population/PopulationHouseholdDetailsPage';
import { PopulationHouseholdPage } from '../pages/population/PopulationHouseholdPage';
import { PopulationIndividualsDetailsPage } from '../pages/population/PopulationIndividualsDetailsPage';
import { PopulationIndividualsPage } from '../pages/population/PopulationIndividualsPage';
import { PeoplePage } from '@containers/pages/people/PeoplePage';
import { PeopleDetailsPage } from '@containers/pages/people/PeopleDetailsPage';
import { HouseholdMembersPage } from '@containers/pages/householdMembers/HouseholdMembersPage';
import { NewTemplatePage } from '@containers/pages/householdMembers/NewTemplatePage';

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
      path: 'population/household-members',
      element: <HouseholdMembersPage />,
    },
    {
      path: 'population/household-members/new-template',
      element: <NewTemplatePage />,
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
