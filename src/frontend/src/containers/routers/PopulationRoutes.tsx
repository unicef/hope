import { useRoutes } from 'react-router-dom';
import { HouseholdMembersPage } from '@containers/pages/population/HouseholdMembersPage';
import { ReactElement } from 'react';
import PeopleDetailsPage from '@containers/pages/people/PeopleDetailsPage';
import PeoplePage from '@containers/pages/people/PeoplePage';
import PopulationHouseholdDetailsPage from '@containers/pages/population/PopulationHouseholdDetailsPage';
import PopulationHouseholdPage from '@containers/pages/population/PopulationHouseholdPage';
import PopulationIndividualsDetailsPage from '@containers/pages/population/PopulationIndividualsDetailsPage';
import PeriodicDataUpdatesOnlineEditsTemplateDetailsPage from '@components/periodicDataUpdates/PeriodicDataUpdatesOnlineEditsTemplateDetailsPage';
import EditAuthorizedUsersOnline from '@components/periodicDataUpdates/EditAuthorizedUsersOnline';
import NewOfflineTemplatePage from '@containers/pages/population/NewOfflineTemplatePage';
import NewOnlineTemplatePage from '@containers/pages/population/NewOnlineTemplatePage';

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
      path: 'population/individuals/new-offline-template',
      element: <NewOfflineTemplatePage />,
    },
    {
      path: 'population/people/new-offline-template',
      element: <NewOfflineTemplatePage />,
    },
    {
      path: 'population/individuals/new-online-template',
      element: <NewOnlineTemplatePage />,
    },
    {
      path: 'population/people/new-online-template',
      element: <NewOnlineTemplatePage />,
    },
    {
      path: 'population/individuals/online-templates/:id',
      element: <PeriodicDataUpdatesOnlineEditsTemplateDetailsPage />,
    },
    {
      path: 'population/individuals/online-templates/:id/edit-authorised-users',
      element: <EditAuthorizedUsersOnline />,
    },
  ];

  return useRoutes(populationRoutes);
};
