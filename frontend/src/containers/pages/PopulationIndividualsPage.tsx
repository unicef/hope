import React, { useState } from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { IndividualsListTable } from '../tables/IndividualsListTable';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { IndividualsFilter } from '../../components/population/IndividualsFilter';
import { useDebounce } from '../../hooks/useDebounce';
import { PermissionDenied } from '../../components/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { usePermissions } from '../../hooks/usePermissions';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PopulationIndividualsPage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const [filter, setFilter] = useState({
    sex: [],
    age: { min: undefined, max: undefined },
  });
  const debouncedFilter = useDebounce(filter, 500);

  if (permissions === null) return null;

  if (
    !hasPermissions(PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST, permissions)
  )
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title='Individuals' />
      <IndividualsFilter filter={filter} onFilterChange={setFilter} />
      <Container data-cy='page-details-container'>
        <IndividualsListTable
          filter={debouncedFilter}
          businessArea={businessArea}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_DETAILS,
            permissions,
          )}
        />
      </Container>
    </>
  );
}
