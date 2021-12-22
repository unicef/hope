import React from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { decodeIdString } from '../../../utils/utils';
import {
  AllIndividualsQuery,
  AllIndividualsQueryVariables,
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
  valuesInner;
  selectedIndividual;
  selectedHousehold;
  setSelectedIndividual;
  setSelectedHousehold;
  ticket?;
  excludedId?;
  withdrawn?: boolean;
}

export const LookUpIndividualTable = ({
  businessArea,
  filter,
  setFieldValue,
  valuesInner,
  selectedIndividual,
  setSelectedIndividual,
  setSelectedHousehold,
  ticket,
  excludedId,
  withdrawn,
}: LookUpIndividualTableProps): React.ReactElement => {
  const handleRadioChange = (individual): void => {
    if (individual.household?.id) {
      setFieldValue('selectedHousehold', individual.household);
      setSelectedHousehold(individual.household);
    }
    setSelectedIndividual(individual);
    setFieldValue('selectedIndividual', individual);
    setFieldValue('identityVerified', false);
  };

  const initialVariables : AllIndividualsQueryVariables = {
    businessArea,
    search: filter.search,
    programs: [decodeIdString(filter.programs)],
    lastRegistrationDate: JSON.stringify(filter.lastRegistrationDate),
    status: filter.status,
    admin2: [decodeIdString(filter?.admin2?.node?.id)],
    sex: [filter.sex],
    householdId: valuesInner.selectedHousehold
      ? decodeIdString(valuesInner.selectedHousehold.id)
      : null,
    excludedId: excludedId || ticket?.individual?.id || null,
  };
  if(withdrawn!==null &&withdrawn!==undefined){
    initialVariables.withdrawn = withdrawn
  }

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
