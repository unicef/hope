import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllFeedbacksQueryVariables,
  FeedbackNode,
  useAllFeedbacksQuery,
} from '../../../__generated__/graphql';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { decodeIdString } from '../../../utils/utils';
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
  const initialVariables: AllFeedbacksQueryVariables = {
    feedbackId: filter.feedbackId,
    issueType: filter.issueType || '',
    createdBy: decodeIdString(filter.createdBy) || '',
    createdAtRange: filter.createdAtRange
      ? JSON.stringify(filter.createdAtRange)
      : '',
  };
  return (
    <TableWrapper>
      <UniversalTable<FeedbackNode, AllFeedbacksQueryVariables>
        headCells={headCells}
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
