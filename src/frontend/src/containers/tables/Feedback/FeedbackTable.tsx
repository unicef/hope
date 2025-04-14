import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllFeedbacksQueryVariables,
  FeedbackNode,
  useAllFeedbacksQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { adjustHeadCells, dateToIsoString, decodeIdString } from '@utils/utils';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './FeedbackTableHeadCells';
import { FeedbackTableRow } from './FeedbackTableRow';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';

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

  const { isAllPrograms, programId } = useBaseUrl();
  const initialVariables: AllFeedbacksQueryVariables = {
    feedbackId: filter.feedbackId,
    issueType: filter.issueType || '',
    createdBy: decodeIdString(filter.createdBy) || '',
    createdAtRange:
      filter.createdAtRangeMin || filter.createdAtRangeMax
        ? JSON.stringify({
            min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
            max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
          })
        : '',
    program: isAllPrograms ? filter.program : programId,
    isActiveProgram: filter.programState === 'active' ? 'true' : '',
  };

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
      <UniversalTable<FeedbackNode, AllFeedbacksQueryVariables>
        headCells={
          isAllPrograms ? headCellsWithProgramColumn : adjustedHeadCells
        }
        title={t('Feedbacks List')}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllFeedbacksQuery}
        queriedObjectName="allFeedbacks"
        defaultOrderBy="createdAt"
        defaultOrderDirection="desc"
        initialVariables={initialVariables}
        renderRow={(row) => (
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
