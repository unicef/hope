import { Box } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import {
  useHouseholdChoiceDataQuery,
  useIndividualChoiceDataQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { PeopleListTable } from '@containers/tables/people/PeopleListTable';
import { PeopleFilter } from '@components/people/PeopleFilter';

const initialFilter = {
  search: '',
  searchType: 'individual_id',
  admin2: '',
  sex: '',
  ageMin: '',
  ageMax: '',
  flags: [],
  orderBy: 'unicef_id',
  status: '',
  lastRegistrationDateMin: '',
  lastRegistrationDateMax: '',
};

export function PeoplePage(): React.ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const { data: householdChoicesData, loading: householdChoicesLoading } =
    useHouseholdChoiceDataQuery();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const { data: individualChoicesData, loading: individualChoicesLoading } =
    useIndividualChoiceDataQuery();

  if (householdChoicesLoading || individualChoicesLoading)
    return <LoadingComponent />;

  if (!individualChoicesData || !householdChoicesData || permissions === null)
    return null;

  if (
    !hasPermissions(PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST, permissions)
  )
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('People')} />
      <PeopleFilter
        filter={filter}
        choicesData={individualChoicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <Box
        display="flex"
        flexDirection="column"
        data-cy="page-details-container"
      >
        <PeopleListTable
          filter={appliedFilter}
          businessArea={businessArea}
          choicesData={householdChoicesData}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_DETAILS,
            permissions,
          )}
        />
      </Box>
    </>
  );
}
