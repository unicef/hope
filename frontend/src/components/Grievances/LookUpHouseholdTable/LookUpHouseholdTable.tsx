import React, { useState } from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import {
  AllHouseholdsQueryVariables,
  HouseholdChoiceDataQuery,
  HouseholdNode,
  useAllHouseholdsQuery,
} from '../../../__generated__/graphql';
import { headCells } from './LookUpHouseholdTableHeadCells';
import { LookUpHouseholdTableRow } from './LookUpHouseholdTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface LookUpHouseholdTableProps {
  businessArea: string;
  filter;
  choicesData: HouseholdChoiceDataQuery;
  setFieldValue;
  initialValues;
}

export const LookUpHouseholdTable = ({
  businessArea,
  filter,
  choicesData,
  setFieldValue,
  initialValues,
}: LookUpHouseholdTableProps): React.ReactElement => {
  const initialVariables: AllHouseholdsQueryVariables = {
    businessArea,
    search: filter.search,
    programs: [filter.programs],
    lastRegistrationDate: JSON.stringify(filter.lastRegistrationDate),
    residenceStatus: filter.residenceStatus,
    admin2: [filter.admin2],
    familySize: JSON.stringify(filter.size),
  };
  if (filter.program) {
    initialVariables.programs = [filter.program];
  }
  const [selectedHousehold, setSelectedHousehold] = useState(
    initialValues.selectedHousehold,
  );
  const handleRadioChange = (event) => {
    setSelectedHousehold(event.target.value);
    setFieldValue('selectedHousehold', event.target.value);
  };
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
            radioChangeHandler={handleRadioChange}
            selectedHousehold={selectedHousehold}
            choicesData={choicesData}
          />
        )}
      />
    </TableWrapper>
  );
};
