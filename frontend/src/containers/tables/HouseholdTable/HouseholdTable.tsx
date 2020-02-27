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
  sizeFilter: { min: number | undefined; max: number | undefined };
  textFilter: string;
  businessArea: string;
}

export const HouseholdTable = ({
  sizeFilter,
  businessArea,
}: HouseholdTableProps): React.ReactElement => {
  const initialVariables:AllHouseholdsQueryVariables = {
    businessArea,
    familySize: JSON.stringify(sizeFilter)
  };

  return (
    <TableWrapper>
      <UniversalTable<HouseholdNode, AllHouseholdsQueryVariables>
        title='Households'
        headCells={headCells}
        query={useAllHouseholdsQuery}
        queriedObjectName='allHouseholds'
        initialVariables={initialVariables}
        renderRow={(row) => <HouseHoldTableRow household={row} />}
      />
    </TableWrapper>
  );
};
