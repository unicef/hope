import React, { useEffect } from 'react';
import styled from 'styled-components';
import {
  AllIndividualsForPopulationTableQuery,
  AllIndividualsForPopulationTableQueryVariables,
  useAllIndividualsForPopulationTableQuery,
  useHouseholdLazyQuery,
} from '../../../../__generated__/graphql';
import { UniversalTable } from '../../../../containers/tables/UniversalTable';
import { decodeIdString } from '../../../../utils/utils';
import { TableWrapper } from '../../../core/TableWrapper';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
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
  noTableStyling = false,
}: LookUpIndividualTableProps): React.ReactElement => {
  const { programId, isAllPrograms } = useBaseUrl();
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
    setSelectedHousehold(individual.household);
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

  const renderTable = (): React.ReactElement => {
    return (
      <UniversalTable<
        AllIndividualsForPopulationTableQuery['allIndividuals']['edges'][number]['node'],
        AllIndividualsForPopulationTableQueryVariables
      >
        headCells={preparedHeadcells}
        allowSort={false}
        rowsPerPageOptions={[5, 10, 15, 20]}
        filterOrderBy={filter.orderBy}
        query={useAllIndividualsForPopulationTableQuery}
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
