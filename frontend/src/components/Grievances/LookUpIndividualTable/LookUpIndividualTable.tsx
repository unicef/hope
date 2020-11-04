import React, { useState } from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { decodeIdString } from '../../../utils/utils';
import {
  AllIndividualsQueryVariables,
  IndividualNode,
  useAllIndividualsQuery,
} from '../../../__generated__/graphql';
import { headCells } from './LookUpIndividualTableHeadCells';
import { LookUpIndividualTableRow } from './LookUpIndividualTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface LookUpIndividualTableProps {
  filter;
  businessArea?: string;
  setFieldValue;
  initialValues;
  valuesInner;
}

export const LookUpIndividualTable = ({
  businessArea,
  filter,
  setFieldValue,
  initialValues,
  valuesInner,
}: LookUpIndividualTableProps): React.ReactElement => {
  const [selectedIndividual, setSelectedIndividual] = useState(
    initialValues.selectedIndividual,
  );
  const handleRadioChange = (event) => {
    setSelectedIndividual(event.target.value);
    setFieldValue('selectedIndividual', event.target.value);
    setFieldValue('identityVerified', false);
  };

  const initialVariables = {
    businessArea,
    search: filter.search,
    programme: filter.programme,
    lastRegistrationDate: JSON.stringify(filter.lastRegistrationDate),
    status: [filter.status],
    admin2: [filter.admin2],
    sex: [filter.sex],
    householdId: valuesInner.selectedHousehold
      ? decodeIdString(valuesInner.selectedHousehold)
      : null,
  };

  return (
    <TableWrapper>
      <UniversalTable<IndividualNode, AllIndividualsQueryVariables>
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllIndividualsQuery}
        queriedObjectName='allIndividuals'
        initialVariables={initialVariables}
        renderRow={(row) => (
          <LookUpIndividualTableRow
            radioChangeHandler={handleRadioChange}
            selectedIndividual={selectedIndividual}
            key={row.id}
            individual={row}
          />
        )}
      />
    </TableWrapper>
  );
};
