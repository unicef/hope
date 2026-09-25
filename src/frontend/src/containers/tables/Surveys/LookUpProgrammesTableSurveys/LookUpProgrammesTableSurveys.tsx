import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTableState } from '@hooks/useTableState';
import styled from 'styled-components';
import type { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { TableWrapper } from '@components/core/TableWrapper';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { headCells } from './LookUpProgrammesHeadCellsSurveys';
import { LookUpProgrammesTableRowSurveys } from './LookUpProgrammesTableRowSurveys';
import { adjustHeadCells } from '@utils/utils';
import { useProgramContext } from 'src/programContext';
import type { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import type { ProgramList } from '@restgenerated/models/ProgramList';

const NoTableStyling = styled.div`
  .MuiPaper-elevation1 {
    box-shadow: none;
    padding: 0 !important;
  }
`;

interface LookUpProgrammesTableSurveysProps {
  businessArea: string;
  filter;
  choicesData: ProgramChoices;
  selectedProgram;
  handleChange: (value) => void;
  setFieldValue;
}

export function LookUpProgrammesTableSurveys({
  businessArea,
  filter,
  choicesData,
  selectedProgram,
  handleChange,
  setFieldValue,
}: LookUpProgrammesTableSurveysProps): ReactElement {
  const { selectedProgram: programFromContext } = useProgramContext();
  const beneficiaryGroup = programFromContext?.beneficiaryGroup;

  const filterVariables = useMemo(
    () => ({
      businessAreaSlug: businessArea,
      search: filter.search,
      startDate: filter.startDate || null,
      endDate: filter.endDate || null,
      status: filter.status !== '' ? filter.status : undefined,
      sector: filter.sector,
      numberOfHouseholdsMax: filter.numberOfHouseholdsMax,
      numberOfHouseholdsMin: filter.numberOfHouseholdsMin || 1,
      budgetMax: filter.budgetMax,
      budgetMin: filter.budgetMin,
      dataCollectingType: filter.dataCollectingType,
    }),
    [
      businessArea,
      filter.search,
      filter.startDate,
      filter.endDate,
      filter.status,
      filter.sector,
      filter.numberOfHouseholdsMin,
      filter.numberOfHouseholdsMax,
      filter.budgetMin,
      filter.budgetMax,
      filter.dataCollectingType,
    ],
  );

  const table = useTableState({
    defaultOrderBy: 'startDate',
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );

  const programsListParams = createApiParams(
    { businessAreaSlug: businessArea },
    listVariables,
  );
  const {
    data: dataPrograms,
    isLoading: isLoadingPrograms,
    isFetching: isFetchingPrograms,
    error: errorPrograms,
  } = useQuery<PaginatedProgramListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsList,
      programsListParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsList(programsListParams),
    placeholderData: keepPreviousData,
    enabled: !!filterVariables.businessAreaSlug,
  });

  const programsCountParams = createApiParams(
    { businessAreaSlug: businessArea },
    filterVariables,
  );
  const { data: countData } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsCountRetrieve,
      programsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsCountRetrieve(programsCountParams),
    enabled: page === 0,
  });

  const itemsCount = usePersistedCount(page, countData);

  const handleRadioChange = (id: string): void => {
    handleChange(id);
    setFieldValue('program', id);
  };

  const replacements = {
    totalHhCount: (_beneficiaryGroup) =>
      `Num. of ${_beneficiaryGroup?.groupLabelPlural}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <NoTableStyling>
      <TableWrapper>
        <UniversalRestTable
          headCells={adjustedHeadCells}
          tableState={table}
          data={dataPrograms}
          isLoading={isLoadingPrograms}
          isFetching={isFetchingPrograms}
          error={errorPrograms}
          itemsCount={itemsCount}
          renderRow={(row: ProgramList) => (
            <LookUpProgrammesTableRowSurveys
              key={row.id}
              program={row}
              choicesData={choicesData}
              radioChangeHandler={handleRadioChange}
              selectedProgram={selectedProgram}
            />
          )}
        />
      </TableWrapper>
    </NoTableStyling>
  );
}
