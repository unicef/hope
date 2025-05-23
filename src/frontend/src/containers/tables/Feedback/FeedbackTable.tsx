import { ReactElement, useMemo, useState } from 'react';
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
import { useQuery } from '@tanstack/react-query';
import { createApiParams } from '@utils/apiUtils';
import { PaginatedFeedbackListList } from '@restgenerated/models/PaginatedFeedbackListList';
import { FeedbackList } from '@restgenerated/models/FeedbackList';
import { CountResponse } from '@restgenerated/models/CountResponse';

interface FeedbackTableProps {
  filter;
  canViewDetails: boolean;
}

function FeedbackTable({
  filter,
  canViewDetails,
}: FeedbackTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { isAllPrograms, programId, businessArea } = useBaseUrl();

  const initialQueryVariables = useMemo(
    () => ({
      feedbackId: filter.feedbackId,
      issueType: filter.issueType || null,
      createdBy: decodeIdString(filter.createdBy) || null,
      createdAtBefore: dateToIsoString(filter.createdAtBefore, 'startOfDay'),
      createdAtAfter: dateToIsoString(filter.createdAtAfter, 'endOfDay'),
      program: isAllPrograms ? filter.program : null,
      isActiveProgram: filter.programState === 'active' ? true : null,
      businessAreaSlug: businessArea,
      programSlug: isAllPrograms ? null : programId,
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

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);

  // Effect to update queryVariables when filters change
  useMemo(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  // Selected Program Feedbacks
  const {
    data: selectedProgramFeedbacksData,
    error: errorSelectedProgram,
    isLoading: isLoadingSelectedProgram,
  } = useQuery<PaginatedFeedbackListList>({
    queryKey: [
      'businessAreasProgramsFeedbacksList',
      queryVariables,
      programId,
      businessArea,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsFeedbacksList(
        createApiParams(
          { businessAreaSlug: businessArea, programSlug: programId },
          queryVariables,
          { withPagination: true },
        ),
      ),
    enabled: !isAllPrograms,
  });

  // Selected Program Count
  const { data: selectedProgramFeedbacksCount } = useQuery<CountResponse>({
    queryKey: [
      'businessAreasProgramsFeedbacksCountRetrieve',
      businessArea,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsFeedbacksCountRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
      }),
    enabled: !isAllPrograms,
  });

  // All Programs Feedbacks
  const {
    data: allProgramsFeedbacksData,
    error: errorAllPrograms,
    isLoading: isLoadingAllPrograms,
  } = useQuery<PaginatedFeedbackListList>({
    queryKey: ['businessAreasFeedbacksList', queryVariables, businessArea],
    queryFn: () => {
      return RestService.restBusinessAreasFeedbacksList(
        createApiParams({ businessAreaSlug: businessArea }, queryVariables, {
          withPagination: true,
        }),
      );
    },
    enabled: isAllPrograms,
  });

  // All Programs Count
  const { data: allProgramsFeedbacksCount } = useQuery<CountResponse>({
    queryKey: ['businessAreasFeedbacksCountRetrieve', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasFeedbacksCountRetrieve({
        businessAreaSlug: businessArea,
      }),
    enabled: isAllPrograms,
  });

  const replacements = {
    household_lookup: (_beneficiaryGroup) =>
      `${_beneficiaryGroup?.groupLabel} ID`,
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

  return (
    <TableWrapper>
      <UniversalRestTable
        headCells={
          isAllPrograms ? headCellsWithProgramColumn : adjustedHeadCells
        }
        title={t('Feedbacks List')}
        rowsPerPageOptions={[10, 15, 20]}
        defaultOrderBy="createdAt"
        defaultOrderDirection="desc"
        queryVariables={queryVariables}
        setQueryVariables={setQueryVariables}
        data={
          isAllPrograms
            ? allProgramsFeedbacksData
            : selectedProgramFeedbacksData
        }
        error={isAllPrograms ? errorAllPrograms : errorSelectedProgram}
        isLoading={
          isAllPrograms ? isLoadingAllPrograms : isLoadingSelectedProgram
        }
        itemsCount={
          isAllPrograms
            ? allProgramsFeedbacksCount?.count
            : selectedProgramFeedbacksCount?.count
        }
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
