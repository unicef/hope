import React from 'react';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { HouseholdTable } from '../HouseholdTable';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

export function PopulationHouseholdPage(): React.ReactElement {
  return (
    <div>
      <PageHeader title='Households' />
      <Container>
        <HouseholdTable />
      </Container>
    </div>
  );
}
