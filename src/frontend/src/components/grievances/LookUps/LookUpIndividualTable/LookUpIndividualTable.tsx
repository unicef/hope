import styled from 'styled-components';
import {
  AllIndividualsForPopulationTableQuery,
  AllIndividualsForPopulationTableQueryVariables,
  IndividualRdiMergeStatus,
  useAllIndividualsForPopulationTableQuery,
} from '@generated/graphql';
import { UniversalTable } from '@containers/tables/UniversalTable';
import { adjustHeadCells, decodeIdString } from '@utils/utils';
import { TableWrapper } from '@core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  headCellsSocialProgram,
  headCellsStandardProgram,
} from './LookUpIndividualTableHeadCells';
import { LookUpIndividualTableRow } from './LookUpIndividualTableRow';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';

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
}: LookUpIndividualTableProps): ReactElement {
  const { isSocialDctType } = useProgramContext();
  const { programId, isAllPrograms } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

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
    documentType: filter.documentType,
    documentNumber: filter.documentNumber.trim(),
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
    withdrawn: false,
    rdiMergeStatus: IndividualRdiMergeStatus.Merged,
  };

  const replacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel} ID`,
    household__id: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} ID`,
  };

  const headCells = isSocialDctType
    ? headCellsSocialProgram
    : headCellsStandardProgram;

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const headCellsWithProgramColumn = [
    ...adjustedHeadCells,
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
    : adjustedHeadCells;

  const renderTable = (): ReactElement => (
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
