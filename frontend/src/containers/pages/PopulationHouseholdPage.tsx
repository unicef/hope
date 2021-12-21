import get from 'lodash/get';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LoadingComponent } from '../../components/LoadingComponent';
import { PageHeader } from '../../components/PageHeader';
import { PermissionDenied } from '../../components/PermissionDenied';
import { HouseholdFilters } from '../../components/Population/HouseholdFilter';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { usePermissions } from '../../hooks/usePermissions';
import {
  ProgramNode,
  useAllProgramsQuery,
  useHouseholdChoiceDataQuery,
} from '../../__generated__/graphql';
import { HouseholdTable } from '../tables/HouseholdTable';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PopulationHouseholdPage(): React.ReactElement {
  const { t } = useTranslation();
  const [filter, setFilter] = useState({
    householdSize: { min: undefined, max: undefined },
  });
  const debouncedFilter = useDebounce(filter, 500);
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery({
    variables: { businessArea },
  });

  if (loading || choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST, permissions))
    return <PermissionDenied />;

  if (!choicesData) return null;

  const allPrograms = get(data, 'allPrograms.edges', []);
  const programs = allPrograms.map((edge) => edge.node);

  return (
    <div>
      <PageHeader title={t('Households')} />
      <HouseholdFilters
        programs={programs as ProgramNode[]}
        filter={filter}
        onFilterChange={setFilter}
        choicesData={choicesData}
      />
      <Container data-cy='page-details-container'>
        <HouseholdTable
          filter={debouncedFilter}
          businessArea={businessArea}
          choicesData={choicesData}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            permissions,
          )}
        />
      </Container>
    </div>
  );
}
