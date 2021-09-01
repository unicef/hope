import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { PermissionDenied } from '../../components/PermissionDenied';
import { IndividualsFilter } from '../../components/population/IndividualsFilter';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { usePermissions } from '../../hooks/usePermissions';
import { IndividualsListTable } from '../tables/IndividualsListTable';
import { useIndividualChoiceDataQuery } from '../../__generated__/graphql';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PopulationIndividualsPage(): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const [filter, setFilter] = useState({
    sex: [],
    age: { min: undefined, max: undefined },
    flags: [],
  });
  const debouncedFilter = useDebounce(filter, 500);
  const { data: choicesData } = useIndividualChoiceDataQuery();

  if (permissions === null) return null;

  if (
    !hasPermissions(PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST, permissions)
  )
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('Individuals')} />
      <IndividualsFilter
        filter={filter}
        onFilterChange={setFilter}
        choicesData={choicesData}
      />
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
