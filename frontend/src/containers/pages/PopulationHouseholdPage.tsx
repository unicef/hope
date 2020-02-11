import React from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { HouseholdTable } from '../HouseholdTable';
import { HouseholdFilters } from '../../components/population/HouseholdFilter';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PopulationHouseholdPage(): React.ReactElement {
  return (
    <div>
      <PageHeader title='Households' />
      <HouseholdFilters />
      <Container>
        <HouseholdTable />
      </Container>
    </div>
  );
}
