import React, { useState } from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { HouseholdFilters } from '../../components/population/HouseholdFilter';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { HouseholdTable } from '../tables/HouseholdTable';
import { useAllProgramsQuery, ProgramNode } from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../../components/BreadCrumbs';
import { useDebounce } from '../../hooks/useDebounce';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PopulationHouseholdPage(): React.ReactElement {
  const [filter, setFilter] = useState({
    householdSize: { min: undefined, max: undefined },
  });
  const debouncedFilter = useDebounce(filter, 500);
  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
  });

  if (loading) return null;


  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);

  return (
    <div>
      <PageHeader title='Households'/>
      <HouseholdFilters
        programs={programs as ProgramNode[]}
        filter={filter}
        onFilterChange={setFilter}
      />
      <Container>
        <HouseholdTable
          filter={debouncedFilter}
          businessArea={businessArea}
        />
      </Container>
    </div>
  );
}
