import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { TableWrapper } from '@core/TableWrapper';
import { IndividualRdiMergeStatus } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { IndividualList } from '@restgenerated/models/IndividualList';
import { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells, decodeIdString } from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useProgramContext } from 'src/programContext';
import { createApiParams } from '@utils/apiUtils';
import styled from 'styled-components';
import {
  headCellsSocialProgram,
  headCellsStandardProgram,
} from './LookUpIndividualTableHeadCells';
import { LookUpIndividualTableRow } from './LookUpIndividualTableRow';
import { CountResponse } from '@restgenerated/models/CountResponse';

interface LookUpIndividualTableProps {
  filter;
  businessArea?: string;
  setFieldValue;
  valuesInner;
  selectedIndividual;
  selectedHousehold: HouseholdDetail;
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
  const { businessArea, programId, isAllPrograms } = useBaseUrl();
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

  const initialQueryVariables = useMemo(
    () => ({
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
    }),
    [
      filter.ageMin,
      filter.ageMax,
      filter.sex,
      filter.search,
      filter.documentType,
      filter.documentNumber,
      filter.admin2,
      filter.flags,
      filter.status,
      filter.lastRegistrationDateMin,
      filter.lastRegistrationDateMax,
      filter.orderBy,
      filter.program,
      filter.programState,
      householdId,
      excludedId,
      ticket?.individual?.id,
      isAllPrograms,
      programId,
    ],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  // Selected Program Individuals
  const {
    data: selectedProgramIndividualsData,
    isLoading: isLoadingSelectedProgram,
    error: errorSelectedProgram,
  } = useQuery<PaginatedIndividualListList>({
    queryKey: [
      'businessAreasProgramsIndividualsList',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      ),
    enabled: !!businessArea && !!programId && !isAllPrograms,
  });

  // Selected Program Count
  const { data: selectedProgramIndividualsCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsIndividualsCountRetrieve',
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
      }),
    enabled: !!businessArea && !!programId && !isAllPrograms,
  });

  // All Programs Individuals
  const {
    data: allProgramsIndividualsData,
    isLoading: isLoadingAllPrograms,
    error: errorAllPrograms,
  } = useQuery<PaginatedIndividualListList>({
    queryKey: ['businessAreasIndividualsList', queryVariables, businessArea],
    queryFn: () => {
      return RestService.restBusinessAreasIndividualsList(
        createApiParams({ businessAreaSlug: businessArea }, queryVariables, {
          withPagination: true,
        }),
      );
    },
    enabled: !!businessArea && isAllPrograms,
  });

  // All Programs Count
  const { data: allProgramsIndividualsCount } = useQuery<CountResponse>({
    queryKey: ['businessAreasIndividualsCountRetrieve', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasIndividualsCountRetrieve({
        businessAreaSlug: businessArea,
      }),
    enabled: !!businessArea && isAllPrograms,
  });

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
    <UniversalRestTable
      headCells={preparedHeadcells}
      allowSort={false}
      rowsPerPageOptions={[5, 10, 15, 20]}
      filterOrderBy={filter.orderBy}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      data={
        isAllPrograms
          ? allProgramsIndividualsData
          : selectedProgramIndividualsData
      }
      error={isAllPrograms ? errorAllPrograms : errorSelectedProgram}
      isLoading={
        isAllPrograms ? isLoadingAllPrograms : isLoadingSelectedProgram
      }
      itemsCount={
        isAllPrograms
          ? allProgramsIndividualsCount?.count
          : selectedProgramIndividualsCount?.count
      }
      renderRow={(row: IndividualList) => (
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
