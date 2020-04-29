import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './TargetPopulationHouseholdHeadCells';
import { TargetPopulationHouseholdTableRow } from './TargetPopulationHouseholdRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface TargetPopulationHouseholdProps {
  id?: string;
  query?;
  queryObjectName?;
  variables?;
}

export const TargetPopulationHouseholdTable = ({
  id,
  query,
  queryObjectName,
  variables,
}: TargetPopulationHouseholdProps): ReactElement => {
  const initialVariables = {
    ...(id && { targetPopulation: id }),
    ...variables
  };
  return (
    <TableWrapper>
      <UniversalTable
        title='Households'
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={query}
        queriedObjectName={queryObjectName}
        initialVariables={initialVariables}
        renderRow={(row) => (
          <TargetPopulationHouseholdTableRow household={row} />
        )}
      />
    </TableWrapper>
  );
};
