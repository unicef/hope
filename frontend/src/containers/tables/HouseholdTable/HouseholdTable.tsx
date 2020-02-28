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
  programFilter: string;
  sizeFilter: { min: number | undefined; max: number | undefined };
  textFilter: string;
  businessArea: string;
}

export const HouseholdTable = ({
  programFilter,
  sizeFilter,
  businessArea,
  textFilter,
}: HouseholdTableProps): React.ReactElement => {
  const initialVariables: AllHouseholdsQueryVariables = {
    businessArea,
    familySize: JSON.stringify(sizeFilter),
    headOfHouseholdFullNameIcontains: textFilter,
    // familySizeGreater: Number(sizeFilter.min),
    // familySizeLower: Number(sizeFilter.max),
  };

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
