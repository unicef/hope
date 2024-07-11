import * as React from 'react';
import { useRoutes } from 'react-router-dom';
import { PopulationHouseholdDetailsPage } from '../pages/population/PopulationHouseholdDetailsPage';
import { PopulationHouseholdPage } from '../pages/population/PopulationHouseholdPage';
import { PopulationIndividualsDetailsPage } from '../pages/population/PopulationIndividualsDetailsPage';
import { PeoplePage } from '@containers/pages/people/PeoplePage';
import { PeopleDetailsPage } from '@containers/pages/people/PeopleDetailsPage';
import { NewTemplatePage } from '@containers/pages/householdMembers/NewTemplatePage';
import { HouseholdMembersPage } from '@containers/pages/population/HouseholdMembersPage';
import { NewTemplatePeoplePage } from '@containers/pages/householdMembers/NewTemplatePeoplePage';

export const PopulationRoutes = (): React.ReactElement => {
  const populationRoutes = [
    {
      path: 'population/household/:id',
      element: <PopulationHouseholdDetailsPage />,
    },
    {
      path: 'population/individuals',
      element: <HouseholdMembersPage />,
    },
    {
      path: 'population/individuals/:id',
      element: <PopulationIndividualsDetailsPage />,
    },
    {
      path: 'population/people',
      element: <PeoplePage />,
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
      path: 'population/individuals/new-template',
      element: <NewTemplatePage />,
    },
    {
      path: 'population/people/new-template',
      element: <NewTemplatePeoplePage />,
    },
  ];

  return useRoutes(populationRoutes);
};
