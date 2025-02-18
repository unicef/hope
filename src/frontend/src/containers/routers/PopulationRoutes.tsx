import { useRoutes } from 'react-router-dom';
import { NewTemplatePage } from '@containers/pages/householdMembers/NewTemplatePage';
import { HouseholdMembersPage } from '@containers/pages/population/HouseholdMembersPage';
import { ReactElement } from 'react';
import PeopleDetailsPage from '@containers/pages/people/PeopleDetailsPage';
import PeoplePage from '@containers/pages/people/PeoplePage';
import PopulationHouseholdDetailsPage from '@containers/pages/population/PopulationHouseholdDetailsPage';
import PopulationHouseholdPage from '@containers/pages/population/PopulationHouseholdPage';
import PopulationIndividualsDetailsPage from '@containers/pages/population/PopulationIndividualsDetailsPage';

export const PopulationRoutes = (): ReactElement => {
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
      element: <NewTemplatePage />,
    },
  ];

  return useRoutes(populationRoutes);
};
