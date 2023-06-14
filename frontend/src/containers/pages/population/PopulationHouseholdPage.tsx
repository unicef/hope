import { Box } from '@material-ui/core';
import get from 'lodash/get';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import {
  ProgramNode,
  useAllProgramsForChoicesQuery,
  useHouseholdChoiceDataQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { HouseholdFilters } from '../../../components/population/HouseholdFilter';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { HouseholdTable } from '../../tables/population/HouseholdTable';

const initialFilter = {
  search: '',
  program: '',
  residenceStatus: '',
  admin2: '',
  householdSizeMin: '',
  householdSizeMax: '',
  orderBy: 'unicef_id',
  withdrawn: null,
};

export const PopulationHouseholdPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

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
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <Box
        display='flex'
        flexDirection='column'
        data-cy='page-details-container'
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
};
