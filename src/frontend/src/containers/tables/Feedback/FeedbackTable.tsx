import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { adjustHeadCells, dateToIsoString, decodeIdString } from '@utils/utils';
import { headCells } from './FeedbackTableHeadCells';
import { FeedbackTableRow } from './FeedbackTableRow';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { RestService } from '@restgenerated/services/RestService';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { createApiParams } from '@utils/apiUtils';
import { PROGRAM_STATE_FILTER } from '@utils/constants';
import type { PaginatedFeedbackListList } from '@restgenerated/models/PaginatedFeedbackListList';
import type { FeedbackList } from '@restgenerated/models/FeedbackList';
import type { CountResponse } from '@restgenerated/models/CountResponse';
import { usePersistedCount } from '@hooks/usePersistedCount';
import { useTableState } from '@hooks/useTableState';

interface FeedbackTableProps {
  filter;
  canViewDetails: boolean;
}

function FeedbackTable({
  filter,
  canViewDetails,
}: FeedbackTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram, isSocialDctType } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { isAllPrograms, programId, businessArea } = useBaseUrl();

  const filterVariables = useMemo(
    () => ({
      feedbackId: filter.feedbackId,
      issueType: filter.issueType || null,
      createdBy: decodeIdString(filter.createdBy) || null,
      createdAtBefore: dateToIsoString(filter.createdAtBefore, 'startOfDay'),
      createdAtAfter: dateToIsoString(filter.createdAtAfter, 'endOfDay'),
      program: isAllPrograms ? filter.program : null,
      isActiveProgram:
        filter.programState === PROGRAM_STATE_FILTER.ACTIVE ? true : null,
      businessAreaSlug: businessArea,
      programCode: isAllPrograms ? null : programId,
    }),
    [
      filter.feedbackId,
      filter.issueType,
      filter.createdBy,
      filter.createdAtBefore,
      filter.createdAtAfter,
      filter.program,
      filter.programState,
      businessArea,
      programId,
      isAllPrograms,
    ],
  );

  const table = useTableState({
    rowsPerPageOptions: [10, 15, 20],
    defaultOrderBy: 'createdAt',
    defaultOrderDirection: 'desc',
    resetPageOn: filterVariables,
  });
  const { page } = table;
  const listVariables = useMemo(
    () => ({ ...filterVariables, ...table.paginationParams }),
    [filterVariables, table.paginationParams],
  );

  const selectedProgramListParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    listVariables,
  );
  const selectedProgramCountParams = createApiParams(
    { businessAreaSlug: businessArea, programCode: programId },
    filterVariables,
  );
  const allProgramsListParams = createApiParams(
    { businessAreaSlug: businessArea },
    listVariables,
  );
  const allProgramsCountParams = createApiParams(
    { businessAreaSlug: businessArea },
    filterVariables,
  );

  // Selected Program Feedbacks
  const {
    data: selectedProgramFeedbacksData,
    error: errorSelectedProgram,
    isLoading: isLoadingSelectedProgram,
    isFetching: isFetchingSelectedProgram,
  } = useQuery<PaginatedFeedbackListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsFeedbacksList,
      selectedProgramListParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsFeedbacksList(
        selectedProgramListParams,
      ),
    enabled: !isAllPrograms,
    placeholderData: keepPreviousData,
  });

  // Selected Program Count
  const { data: selectedProgramFeedbacksCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsFeedbacksCountRetrieve,
      selectedProgramCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsFeedbacksCountRetrieve(
        selectedProgramCountParams,
      ),
    enabled: !isAllPrograms && page === 0,
  });

  // All Programs Feedbacks
  const {
    data: allProgramsFeedbacksData,
    error: errorAllPrograms,
    isLoading: isLoadingAllPrograms,
    isFetching: isFetchingAllPrograms,
  } = useQuery<PaginatedFeedbackListList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasFeedbacksList,
      allProgramsListParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasFeedbacksList(allProgramsListParams),
    enabled: isAllPrograms,
    placeholderData: keepPreviousData,
  });

  // All Programs Count
  const { data: allProgramsFeedbacksCount } = useQuery<CountResponse>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasFeedbacksCountRetrieve,
      allProgramsCountParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasFeedbacksCountRetrieve(
        allProgramsCountParams,
      ),
    enabled: isAllPrograms && page === 0,
  });

  const replacements = {
    household_lookup: (_beneficiaryGroup) =>
      isSocialDctType ? 'Target ID' : `${_beneficiaryGroup?.groupLabel} ID`,
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

  const itemsCount = usePersistedCount(
    page,
    isAllPrograms ? allProgramsFeedbacksCount : selectedProgramFeedbacksCount,
  );

  return (
    <TableWrapper>
      <UniversalRestTable
        headCells={
          isAllPrograms ? headCellsWithProgramColumn : adjustedHeadCells
        }
        title={t('Feedbacks List')}
        tableState={table}
        data={
          isAllPrograms
            ? allProgramsFeedbacksData
            : selectedProgramFeedbacksData
        }
        error={isAllPrograms ? errorAllPrograms : errorSelectedProgram}
        isLoading={
          isAllPrograms ? isLoadingAllPrograms : isLoadingSelectedProgram
        }
        isFetching={
          isAllPrograms ? isFetchingAllPrograms : isFetchingSelectedProgram
        }
        itemsCount={itemsCount}
        renderRow={(row: FeedbackList) => (
          <FeedbackTableRow
            key={row.id}
            feedback={row}
            canViewDetails={canViewDetails}
          />
        )}
      />
    </TableWrapper>
  );
}

export default withErrorBoundary(FeedbackTable, 'FeedbackTable');
