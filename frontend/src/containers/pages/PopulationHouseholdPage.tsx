import React, { useState } from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { HouseholdTable } from '../HouseholdTable';
import { HouseholdFilters } from '../../components/population/HouseholdFilter';
import { useBusinessArea } from '../../hooks/useBusinessArea';

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
  const businessArea = useBusinessArea();

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

  const handleTextFilter = (value: string): void => {
    if (value.length > 3) {
      setTextFilter(value);
    } else {
      setTextFilter('');
    }
  };

  return (
    <div>
      <PageHeader title='Households' />
      <HouseholdFilters
        minValue={sizeFilter.min}
        maxValue={sizeFilter.max}
        householdMaxSizeFilter={handleMaxSizeFilter}
        householdMinSizeFilter={handleMinSizeFilter}
        householdTextFilter={handleTextFilter}
      />
      <Container>
        <HouseholdTable
          sizeFilter={sizeFilter}
          textFilter={textFilter}
          businessArea={businessArea}
        />
      </Container>
    </div>
  );
}
