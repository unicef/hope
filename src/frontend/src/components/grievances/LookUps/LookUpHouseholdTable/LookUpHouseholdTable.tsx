import { MouseEvent, ReactElement, useState } from 'react';
import styled from 'styled-components';
import {
  AllHouseholdsForPopulationTableQuery,
  AllHouseholdsForPopulationTableQueryVariables,
  HouseholdChoiceDataQuery,
  useAllHouseholdsForPopulationTableQuery,
} from '@generated/graphql';
import { UniversalTable } from '@containers/tables/UniversalTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { TableWrapper } from '@core/TableWrapper';
import { headCells } from './LookUpHouseholdTableHeadCells';
import { LookUpHouseholdTableRow } from './LookUpHouseholdTableRow';
import { useProgramContext } from 'src/programContext';
import { adjustHeadCells } from '@utils/utils';

interface LookUpHouseholdTableProps {
  businessArea: string;
  filter;
  choicesData: HouseholdChoiceDataQuery;
  setFieldValue;
  selectedHousehold?;
  setSelectedIndividual?;
  setSelectedHousehold?;
  noTableStyling?;
  householdMultiSelect?: boolean;
  redirectedFromRelatedTicket?: boolean;
  isFeedbackWithHouseholdOnly?: boolean;
}

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

export function LookUpHouseholdTable({
  businessArea,
  filter,
  choicesData,
  setFieldValue,
  selectedHousehold,
  setSelectedIndividual,
  setSelectedHousehold,
  noTableStyling = false,
  householdMultiSelect,
  redirectedFromRelatedTicket,
  isFeedbackWithHouseholdOnly,
}: LookUpHouseholdTableProps): ReactElement {
  const { isAllPrograms, programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const matchWithdrawnValue = (): boolean | undefined => {
    if (filter.withdrawn === 'true') {
      return true;
    }
    if (filter.withdrawn === 'false') {
      return false;
    }
    return undefined;
  };
  const initialVariables: AllHouseholdsForPopulationTableQueryVariables = {
    businessArea,
    familySize: JSON.stringify({
      min: filter.householdSizeMin,
      max: filter.householdSizeMax,
    }),
    search: filter.search.trim(),
    documentType: filter.documentType,
    documentNumber: filter.documentNumber.trim(),
    admin1: filter.admin1,
    admin2: filter.admin2,
    residenceStatus: filter.residenceStatus,
    withdrawn: matchWithdrawnValue(),
    orderBy: filter.orderBy,
    program: isAllPrograms ? filter.program : programId,
    isActiveProgram: filter.programState === 'active' ? true : null,
  };

  const [selected, setSelected] = useState<string[]>(
    householdMultiSelect ? [...selectedHousehold] : [selectedHousehold],
  );

  const handleCheckboxClick = (
    _event: MouseEvent<HTMLTableRowElement> | MouseEvent<HTMLButtonElement>,
    name: string,
  ): void => {
    const selectedIndex = selected.indexOf(name);
    const newSelected = [...selected];

    if (selectedIndex === -1) {
      newSelected.push(name);
    } else {
      newSelected.splice(selectedIndex, 1);
    }

    if (setSelectedIndividual === undefined && householdMultiSelect) {
      setSelectedHousehold(newSelected);
    }
    setSelected(newSelected);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    event.preventDefault();
    let newSelecteds = [];
    if (!selected.length) {
      newSelecteds = rows.map((row) => row.id);
      setSelected(newSelecteds);
    } else {
      setSelected([]);
    }
    if (setSelectedIndividual === undefined && householdMultiSelect) {
      setSelectedHousehold(newSelecteds);
    }
  };

  const handleRadioChange = (
    household: AllHouseholdsForPopulationTableQuery['allHouseholds']['edges'][number]['node'],
  ): void => {
    setSelectedHousehold(household);
    setFieldValue('selectedHousehold', household);
    setFieldValue('selectedIndividual', null);
    if (setSelectedIndividual !== undefined) {
      setSelectedIndividual(null);
    }
    setFieldValue('identityVerified', false);
  };

  const replacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} ID`,
    head_of_household__full_name: (_beneficiaryGroup) =>
      `Head of ${_beneficiaryGroup?.groupLabel}`,
    size: (_beneficiaryGroup) => `${_beneficiaryGroup?.groupLabel} Size`,
  };

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
      id: 'programs',
      numeric: false,
      dataCy: 'programs',
    },
  ];

  const preparedHeadcells = isAllPrograms
    ? headCellsWithProgramColumn
    : adjustedHeadCells;

  const renderTable = (): ReactElement => (
    <UniversalTable<
      AllHouseholdsForPopulationTableQuery['allHouseholds']['edges'][number]['node'],
      AllHouseholdsForPopulationTableQueryVariables
    >
      headCells={
        householdMultiSelect ? preparedHeadcells.slice(1) : preparedHeadcells
      }
      rowsPerPageOptions={[5, 10, 15, 20]}
      query={useAllHouseholdsForPopulationTableQuery}
      queriedObjectName="allHouseholds"
      initialVariables={initialVariables}
      allowSort={false}
      filterOrderBy={filter.orderBy}
      onSelectAllClick={householdMultiSelect && handleSelectAllCheckboxesClick}
      numSelected={householdMultiSelect && selected.length}
      renderRow={(row) => (
        <LookUpHouseholdTableRow
          key={row.id}
          household={row}
          radioChangeHandler={handleRadioChange}
          selectedHousehold={selectedHousehold}
          choicesData={choicesData}
          checkboxClickHandler={handleCheckboxClick}
          selected={selected}
          householdMultiSelect={householdMultiSelect}
          redirectedFromRelatedTicket={redirectedFromRelatedTicket}
          isFeedbackWithHouseholdOnly={isFeedbackWithHouseholdOnly}
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
