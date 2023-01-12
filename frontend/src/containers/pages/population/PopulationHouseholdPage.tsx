import { Box } from '@material-ui/core';
import get from 'lodash/get';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { HouseholdFilters } from '../../../components/population/HouseholdFilter';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import {
  ProgramNode,
  useAllProgramsForChoicesQuery,
  useHouseholdChoiceDataQuery,
} from '../../../__generated__/graphql';
import { HouseholdTable } from '../../tables/population/HouseholdTable';

export const PopulationHouseholdPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const [filter, setFilter] = useState({
    text: '',
    program: '',
    residenceStatus: '',
    householdSize: { min: '', max: '' },
    orderBy: 'unicef_id',
  });
  const debouncedFilter = useDebounce(filter, 500);
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery({
    variables: { businessArea },
    fetchPolicy: 'cache-first',
  });

  if (loading || choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST, permissions))
    return <PermissionDenied />;

  if (!choicesData) return null;

  const allPrograms = get(data, 'allPrograms.edges', []);
  const programs = allPrograms.map((edge) => edge.node);

  return (
    <>
      <PageHeader title={t('Households')} />
      <HouseholdFilters
        programs={programs as ProgramNode[]}
        filter={filter}
        onFilterChange={setFilter}
        choicesData={choicesData}
      />
      <Box
        display='flex'
        flexDirection='column'
        data-cy='page-details-container'
      >
        <HouseholdTable
          filter={debouncedFilter}
          businessArea={businessArea}
          choicesData={choicesData}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            permissions,
          )}
          filterOrderBy={filter.orderBy}
        />
      </Box>
    </>
  );
};
