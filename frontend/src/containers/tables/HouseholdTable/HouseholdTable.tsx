import React from 'react';
import styled from 'styled-components';
import {
  AllHouseholdsQueryVariables,
  HouseholdNode,
  useAllHouseholdsQuery,
} from '../../../__generated__/graphql';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './HouseholdTableHeadCells';
import { HouseHoldTableRow } from './HouseholdTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface HouseholdTableProps {
  businessArea: string;
  filter;
}

export const HouseholdTable = ({
  businessArea,
  filter,
}: HouseholdTableProps): React.ReactElement => {
  const initialVariables: AllHouseholdsQueryVariables = {
    businessArea,
    familySize: JSON.stringify(filter.householdSize),
    headOfHouseholdFullNameIcontains: filter.text,
  };
  if (filter.program) {
    initialVariables.programs = [filter.program];
  }

  return (
    <TableWrapper>
      <UniversalTable<HouseholdNode, AllHouseholdsQueryVariables>
        title='Households'
        headCells={headCells}
        rowsPage={[10, 15, 20]}
        query={useAllHouseholdsQuery}
        queriedObjectName='allHouseholds'
        initialVariables={initialVariables}
        renderRow={(row) => <HouseHoldTableRow household={row} />}
      />
    </TableWrapper>
  );
};
