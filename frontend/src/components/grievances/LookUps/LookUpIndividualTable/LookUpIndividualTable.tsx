import React, { useEffect } from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../../../../containers/tables/UniversalTable';
import { decodeIdString } from '../../../../utils/utils';
import {
  AllIndividualsQuery,
  AllIndividualsQueryVariables,
  useAllIndividualsQuery,
  useHouseholdLazyQuery,
} from '../../../../__generated__/graphql';
import { TableWrapper } from '../../../core/TableWrapper';
import { headCells } from './LookUpIndividualTableHeadCells';
import { LookUpIndividualTableRow } from './LookUpIndividualTableRow';

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
  noTableStyling?;
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

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
  noTableStyling = false,
}: LookUpIndividualTableProps): React.ReactElement => {
  const [getHousehold, results] = useHouseholdLazyQuery();

  useEffect(() => {
    if (results.data && !results.loading && !results.error) {
      setFieldValue('selectedHousehold', results.data.household);
      setSelectedHousehold(results.data.household);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [results, setSelectedHousehold]);

  const handleRadioChange = (individual): void => {
    if (individual.household?.id) {
      getHousehold({ variables: { id: individual.household.id.toString() } });
    }
    setSelectedIndividual(individual);
    setFieldValue('selectedIndividual', individual);
    setFieldValue('identityVerified', false);
  };
  let householdId;
  if ('household' in filter) {
    householdId = decodeIdString(filter.household);
  } else {
    householdId = valuesInner.selectedHousehold
      ? decodeIdString(valuesInner.selectedHousehold.id)
      : null;
  }
  const initialVariables: AllIndividualsQueryVariables = {
    businessArea,
    search: filter.search,
    programs: [decodeIdString(filter.programs)],
    lastRegistrationDate: JSON.stringify(filter.lastRegistrationDate),
    status: filter.status,
    admin2: [decodeIdString(filter?.admin2?.node?.id)],
    sex: [filter.sex],
    householdId,
    excludedId: excludedId || ticket?.individual?.id || null,
  };
  if (withdrawn !== null && withdrawn !== undefined) {
    initialVariables.withdrawn = withdrawn;
  }
  const renderTable = (): React.ReactElement => {
    return (
      <UniversalTable<
        AllIndividualsQuery['allIndividuals']['edges'][number]['node'],
        AllIndividualsQueryVariables
      >
        headCells={headCells}
        rowsPerPageOptions={[5, 10, 15, 20]}
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
    );
  };
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    <TableWrapper>{renderTable()}</TableWrapper>
  );
};
