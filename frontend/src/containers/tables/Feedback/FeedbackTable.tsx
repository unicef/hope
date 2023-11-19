import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllFeedbacksQueryVariables,
  FeedbackNode,
  useAllFeedbacksQuery,
} from '../../../__generated__/graphql';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { dateToIsoString, decodeIdString } from '../../../utils/utils';
import { UniversalTable } from '../UniversalTable';
import { headCells } from './FeedbackTableHeadCells';
import { FeedbackTableRow } from './FeedbackTableRow';

interface FeedbackTableProps {
  filter;
  canViewDetails: boolean;
}

export const FeedbackTable = ({
  filter,
  canViewDetails,
}: FeedbackTableProps): ReactElement => {
  const { t } = useTranslation();
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
    isActiveProgram: filter.programState === 'active' ? true : null,
  };

  const headCellsWithProgramColumn = [
    ...headCells,
    {
      disablePadding: false,
      label: 'Programmes',
      id: 'programs',
      numeric: false,
      dataCy: 'programs',
    },
  ];

  return (
    <TableWrapper>
      <UniversalTable<FeedbackNode, AllFeedbacksQueryVariables>
        headCells={isAllPrograms ? headCellsWithProgramColumn : headCells}
        title={t('Feedbacks List')}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllFeedbacksQuery}
        queriedObjectName='allFeedbacks'
        defaultOrderBy='createdAt'
        defaultOrderDirection='desc'
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
};
