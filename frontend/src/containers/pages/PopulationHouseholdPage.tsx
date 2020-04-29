import React, { useState } from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { HouseholdFilters } from '../../components/population/HouseholdFilter';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { HouseholdTable } from '../tables/HouseholdTable';
import {
  ProgramNode,
  useAllProgramsQuery,
  useHouseholdChoiceDataQuery,
} from '../../__generated__/graphql';
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
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery({
    variables: { businessArea },
  });
  if (loading || choicesLoading) return null;

  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);

  return (
    <div>
      <PageHeader title='Households' />
      <HouseholdFilters
        programs={programs as ProgramNode[]}
        filter={filter}
        onFilterChange={setFilter}
        choicesData={choicesData}
      />
      <Container>
        <HouseholdTable
          filter={debouncedFilter}
          businessArea={businessArea}
          choicesData={choicesData}
        />
      </Container>
    </div>
  );
}
