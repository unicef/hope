import { useRoutes, Navigate } from 'react-router-dom';
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
      path: 'population',
      children: [
        {
          path: 'household/:id',
          element: <PopulationHouseholdDetailsPage />,
        },
        {
          path: 'individuals',
          element: <HouseholdMembersPage />,
        },
        {
          path: 'individuals/:id',
          element: <PopulationIndividualsDetailsPage />,
        },
        {
          path: 'people',
          element: <PeoplePage />,
        },
        {
          path: 'people/:id',
          element: <PeopleDetailsPage />,
        },
        {
          path: 'household',
          element: <PopulationHouseholdPage />,
        },
        {
          path: 'individuals/new-offline-template',
          element: <NewOfflineTemplatePage />,
        },
        {
          path: 'people/new-offline-template',
          element: <NewOfflineTemplatePage />,
        },
        {
          path: 'individuals/new-online-template',
          element: <NewOnlineTemplatePage />,
        },
        {
          path: 'people/new-online-template',
          element: <NewOnlineTemplatePage />,
        },
        {
          path: 'individuals/online-templates/:id',
          element: <PeriodicDataUpdatesOnlineEditsTemplateDetailsPage />,
        },
        {
          path: 'individuals/online-templates/:id/edit-authorised-users',
          element: <EditAuthorizedUsersOnline />,
        },
        {
          path: '*',
          element: <Navigate to="/404" replace />,
        },
      ],
    },
  ];

  return useRoutes(populationRoutes);
};
