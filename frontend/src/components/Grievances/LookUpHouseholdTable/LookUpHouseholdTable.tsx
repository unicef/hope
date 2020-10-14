import React from 'react';
import styled from 'styled-components';
import { headCells } from './LookUpHouseholdTableHeadCells';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import {
  AllHouseholdsQueryVariables,
  HouseholdChoiceDataQuery,
  HouseholdNode,
  useAllHouseholdsQuery,
} from '../../../__generated__/graphql';

import { LookUpHouseholdTableRow } from './LookUpHouseholdTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface LookUpHouseholdTableProps {
  businessArea: string;
  filter;
  choicesData: HouseholdChoiceDataQuery;
}

export const LookUpHouseholdTable = ({
  businessArea,
  filter,
  choicesData,
}: LookUpHouseholdTableProps): React.ReactElement => {
  const initialVariables: AllHouseholdsQueryVariables = {
    businessArea,
    familySize: JSON.stringify(filter.householdSize),
    search: filter.text,
    adminArea: filter.adminArea,
    residenceStatus: filter.residenceStatus,
  };
  if (filter.program) {
    initialVariables.programs = [filter.program];
  }

  return (
    <TableWrapper>
      <UniversalTable<HouseholdNode, AllHouseholdsQueryVariables>
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllHouseholdsQuery}
        queriedObjectName='allHouseholds'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <LookUpHouseholdTableRow
            key={row.id}
            household={row}
            choicesData={choicesData}
          />
        )}
      />
    </TableWrapper>
  );
};
