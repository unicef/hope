import React, { useState } from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { decodeIdString } from '../../../utils/utils';
import {
  AllIndividualsQuery,
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
  const handleRadioChange = (individual): void => {
    setSelectedIndividual(individual);
    setFieldValue('selectedIndividual', individual);
    setFieldValue('identityVerified', false);
  };

  const initialVariables = {
    businessArea,
    search: filter.search,
    programs: [decodeIdString(filter.programs)],
    lastRegistrationDate: JSON.stringify(filter.lastRegistrationDate),
    status: [filter.status],
    admin2: [decodeIdString(filter.admin2)],
    sex: [filter.sex],
    householdId: valuesInner.selectedHousehold
      ? decodeIdString(valuesInner.selectedHousehold.id)
      : null,
  };

  return (
    <TableWrapper>
      <UniversalTable<
        AllIndividualsQuery['allIndividuals']['edges'][number]['node'],
        AllIndividualsQueryVariables
      >
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
