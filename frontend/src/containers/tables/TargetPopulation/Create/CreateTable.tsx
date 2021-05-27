import React, {ReactElement} from 'react';
import styled from 'styled-components';
import {useGoldenRecordByTargetingCriteriaQuery} from '../../../../__generated__/graphql';
import {UniversalTable} from '../../UniversalTable';
import {headCells} from './HeadCells';
import {TargetPopulationHouseholdTableRow} from './TableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface TargetPopulationHouseholdProps {
  id?: string;
  variables?;
  program: string;
  businessArea: string;
}

export const CreateTable = ({
  id = null,
  variables,
  program,
  businessArea,
}: TargetPopulationHouseholdProps): ReactElement => {
  const initialVariables = {
    ...(id && { targetPopulation: id }),
    ...variables,
    program,
    businessArea,
  };
  return (
    <TableWrapper>
      <UniversalTable
        title='Households'
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useGoldenRecordByTargetingCriteriaQuery}
        queriedObjectName='goldenRecordByTargetingCriteria'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <TargetPopulationHouseholdTableRow household={row} />
        )}
      />
    </TableWrapper>
  );
};
