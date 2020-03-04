import React, { useState } from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { IndividualsListTable } from '../tables/IndividualsListTable';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { IndividualsFilter } from '../../components/population/IndividualsFilter';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useDebounce } from '../../hooks/useDebounce';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PopulationIndividualsPage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const [filter, setFilter] = useState({
    age: { min: undefined, max: undefined },
  });
  const debouncedFilter = useDebounce(filter, 500);

  return (
    <>
      <PageHeader title='Individuals' />
      <IndividualsFilter filter={filter} onFilterChange={setFilter} />
      <Container>
        <IndividualsListTable
          filter={debouncedFilter}
          businessArea={businessArea}
        />
      </Container>
    </>
  );
}
