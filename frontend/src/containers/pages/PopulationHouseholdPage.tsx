import React, { useState } from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { HouseholdFilters } from '../../components/population/HouseholdFilter';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { HouseholdTable } from '../tables/HouseholdTable';
import { useAllProgramsQuery, ProgramNode } from '../../__generated__/graphql';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PopulationHouseholdPage(): React.ReactElement {
  const [sizeFilter, setSizeFilter] = useState({
    min: undefined,
    max: undefined,
  });
  const [textFilter, setTextFilter] = useState('');
  const [programFilter, setProgramFilter] = useState();
  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
  });

  if (loading) return null;

  const handleMinSizeFilter = (value: number): void => {
    setSizeFilter({ ...sizeFilter, min: value });
  };
  const handleMaxSizeFilter = (value: number): void => {
    if (value < sizeFilter.min) {
      setSizeFilter({ ...sizeFilter, max: Number(sizeFilter.min) });
    } else {
      setSizeFilter({ ...sizeFilter, max: value });
    }
  };

  const householdProgramFilter = (value: string): void => {
    setProgramFilter(value);
  };

  const handleTextFilter = (value: string): void => {
    if (value.length > 3) {
      setTextFilter(value);
    } else {
      setTextFilter('');
    }
  };

  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);

  return (
    <div>
      <PageHeader title='Households' />
      <HouseholdFilters
        programs={programs as ProgramNode[]}
        minValue={sizeFilter.min}
        maxValue={sizeFilter.max}
        householdProgramFilter={householdProgramFilter}
        householdMaxSizeFilter={handleMaxSizeFilter}
        householdMinSizeFilter={handleMinSizeFilter}
        householdTextFilter={handleTextFilter}
      />
      <Container>
        <HouseholdTable
          programFilter={programFilter}
          sizeFilter={sizeFilter}
          textFilter={textFilter}
          businessArea={businessArea}
        />
      </Container>
    </div>
  );
}
