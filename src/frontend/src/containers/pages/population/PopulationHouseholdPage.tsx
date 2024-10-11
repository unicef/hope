import { Box } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useHouseholdChoiceDataQuery } from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { HouseholdFilters } from '@components/population/HouseholdFilter';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { HouseholdTable } from '../../tables/population/HouseholdTable';

export function PopulationHouseholdPage(): React.ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const { data: choicesData, loading: choicesLoading } =
    useHouseholdChoiceDataQuery({
      fetchPolicy: 'cache-first',
    });
  const initialFilter = {
    search: '',
    documentType: choicesData?.documentTypeChoices?.[0]?.value,
    documentNumber: '',
    residenceStatus: '',
    admin1: '',
    admin2: '',
    householdSizeMin: '',
    householdSizeMax: '',
    orderBy: 'unicef_id',
    withdrawn: '',
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();

  if (choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST, permissions))
    return <PermissionDenied />;

  if (!choicesData) return null;

  return (
    <>
      <PageHeader title={t('Households')} />
      <HouseholdFilters
        filter={filter}
        choicesData={choicesData}
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
        <HouseholdTable
          filter={appliedFilter}
          businessArea={businessArea}
          choicesData={choicesData}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            permissions,
          )}
        />
      </Box>
    </>
  );
}
