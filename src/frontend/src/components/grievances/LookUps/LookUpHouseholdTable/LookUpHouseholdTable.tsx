import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { TableWrapper } from '@core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells } from '@utils/utils';
import { MouseEvent, ReactElement, useEffect, useMemo, useState } from 'react';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { createApiParams } from '@utils/apiUtils';
import { headCells } from './LookUpHouseholdTableHeadCells';
import { LookUpHouseholdTableRow } from './LookUpHouseholdTableRow';
import { PaginatedHouseholdListList } from '@restgenerated/models/PaginatedHouseholdListList';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { CountResponse } from '@restgenerated/models/CountResponse';
import { HouseholdRdiMergeStatus } from '@generated/graphql';

interface LookUpHouseholdTableProps {
  businessArea: string;
  filter;
  choicesData: HouseholdChoices;
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

  const initialQueryVariables = useMemo(() => {
    const matchWithdrawnValue = (): boolean | undefined => {
      if (filter.withdrawn === 'true') {
        return true;
      }
      if (filter.withdrawn === 'false') {
        return false;
      }
      return undefined;
    };

    return {
      businessAreaSlug: businessArea,
      programSlug: programId,
      familySize: JSON.stringify({
        before: filter.householdSizeMin,
        after: filter.householdSizeMax,
      }),
      search: filter.search.trim(),
      documentType: filter.documentType,
      documentNumber: filter.documentNumber.trim(),
      admin1: filter.admin1,
      admin2: filter.admin2,
      residenceStatus: filter.residenceStatus,
      withdrawn: matchWithdrawnValue(),
      rdiMergeStatus: HouseholdRdiMergeStatus.Merged,
    };
  }, [
    businessArea,
    programId,
    filter.householdSizeMin,
    filter.householdSizeMax,
    filter.search,
    filter.documentType,
    filter.documentNumber,
    filter.admin1,
    filter.admin2,
    filter.residenceStatus,
    filter.withdrawn,
  ]);

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  //selectedProgram
  const {
    data: dataHouseholdsProgram,
    isLoading: isLoadingHouseholdsProgram,
    error: errorHouseholdsProgram,
  } = useQuery<PaginatedHouseholdListList>({
    queryKey: [
      'businessAreasProgramsHouseholdsList',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      ),
    enabled: !!businessArea && !!programId,
  });

  //selectedProgram
  const { data: dataHouseholdsProgramCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsHouseholdsCountRetrieve',
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
      }),
  });

  //allPrograms
  const {
    data: dataHouseholdsAllPrograms,
    isLoading: isLoadingHouseholdsAllPrograms,
    error: errorHouseholdsAllPrograms,
  } = useQuery<PaginatedHouseholdListList>({
    queryKey: [
      'businessAreasHouseholdsList',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () => {
      // eslint-disable-next-line no-unused-vars
      const { programSlug, ...restQueryVariables } = queryVariables;
      return RestService.restBusinessAreasHouseholdsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          restQueryVariables,
          { withPagination: true },
        ),
      );
    },
    enabled: !!businessArea && isAllPrograms,
  });
  //allPrograms

  const { data: dataHouseholdsAllProgramsCount } = useQuery<CountResponse>({
    queryKey: ['businessAreasHouseholdsCountRetrieve', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasHouseholdsCountRetrieve({
        businessAreaSlug: businessArea,
      }),
  });
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

  const handleRadioChange = (household): void => {
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
    <UniversalRestTable
      renderRow={(row: PaginatedHouseholdListList['results'][number]) =>
        row ? (
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
        ) : (
          <></>
        )
      }
      itemsCount={
        isAllPrograms
          ? dataHouseholdsAllProgramsCount?.count
          : dataHouseholdsProgramCount?.count
      }
      headCells={
        householdMultiSelect ? preparedHeadcells.slice(1) : preparedHeadcells
      }
      allowSort={false}
      onSelectAllClick={householdMultiSelect && handleSelectAllCheckboxesClick}
      numSelected={householdMultiSelect && selected.length}
      data={isAllPrograms ? dataHouseholdsAllPrograms : dataHouseholdsProgram}
      error={
        isAllPrograms ? errorHouseholdsAllPrograms : errorHouseholdsProgram
      }
      isLoading={
        isAllPrograms
          ? isLoadingHouseholdsAllPrograms
          : isLoadingHouseholdsProgram
      }
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
    />
  );
  return noTableStyling ? (
    <NoTableStyling>{renderTable()}</NoTableStyling>
  ) : (
    <TableWrapper>{renderTable()}</TableWrapper>
  );
}
