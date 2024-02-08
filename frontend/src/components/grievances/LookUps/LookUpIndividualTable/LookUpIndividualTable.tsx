import * as React from 'react';
import styled from 'styled-components';
import {
  AllIndividualsForPopulationTableQuery,
  AllIndividualsForPopulationTableQueryVariables,
  useAllIndividualsForPopulationTableQuery,
} from '@generated/graphql';
import { UniversalTable } from '@containers/tables/UniversalTable';
import { decodeIdString } from '@utils/utils';
import { TableWrapper } from '@core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
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
  noTableStyling?;
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

export function LookUpIndividualTable({
  businessArea,
  filter,
  setFieldValue,
  valuesInner,
  selectedIndividual,
  setSelectedIndividual,
  setSelectedHousehold,
  ticket,
  excludedId,
  noTableStyling = false,
}: LookUpIndividualTableProps): React.ReactElement {
  const { programId, isAllPrograms } = useBaseUrl();

  const handleRadioChange = (individual): void => {
    setSelectedIndividual(individual);

    if (individual.household) {
      setSelectedHousehold(individual.household);
      setFieldValue('selectedHousehold', individual.household);
    }
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

  const initialVariables: AllIndividualsForPopulationTableQueryVariables = {
    businessArea,
    age: JSON.stringify({ min: filter.ageMin, max: filter.ageMax }),
    sex: [filter.sex],
    search: filter.search.trim(),
    searchType: filter.searchType,
    admin2: [filter.admin2],
    flags: filter.flags,
    status: filter.status,
    lastRegistrationDate: JSON.stringify({
      min: filter.lastRegistrationDateMin,
      max: filter.lastRegistrationDateMax,
    }),
    orderBy: filter.orderBy,
    householdId,
    excludedId: excludedId || ticket?.individual?.id || null,
    program: isAllPrograms ? filter.program : programId,
    isActiveProgram: filter.programState === 'active' ? true : null,
  };

  const headCellsWithProgramColumn = [
    ...headCells,
    {
      disablePadding: false,
      label: 'Programme',
      id: 'household__programme',
      numeric: false,
      dataCy: 'individual-programme',
    },
  ];

  const preparedHeadcells = isAllPrograms
    ? headCellsWithProgramColumn
    : headCells;

  const renderTable = (): React.ReactElement => (
    <UniversalTable<
      AllIndividualsForPopulationTableQuery['allIndividuals']['edges'][number]['node'],
      AllIndividualsForPopulationTableQueryVariables
    >
      headCells={preparedHeadcells}
      allowSort={false}
      rowsPerPageOptions={[5, 10, 15, 20]}
      filterOrderBy={filter.orderBy}
      query={useAllIndividualsForPopulationTableQuery}
      queriedObjectName="allIndividuals"
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
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    <TableWrapper>{renderTable()}</TableWrapper>
  );
}
