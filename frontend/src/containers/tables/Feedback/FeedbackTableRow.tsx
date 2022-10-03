import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { FeedbackNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../components/core/UniversalMoment';
import { BlackLink } from '../../../components/core/BlackLink';
import { renderSomethingOrDash, renderUserName } from '../../../utils/utils';

interface FeedbackTableRowProps {
  feedback: FeedbackNode;
  canViewDetails: boolean;
}

export const FeedbackTableRow = ({
  feedback,
  canViewDetails,
}: FeedbackTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const feedbackDetailsPath = `/${businessArea}/accountability/feedback/${feedback.id}`;
  const householdDetailsPath = `/${businessArea}/population/households/${feedback.householdLookup?.id}`;
  const grievanceDetailsPath = `/${businessArea}/grievance-and-feedback/${feedback.linkedGrievance?.id}`;

  const handleClick = (): void => {
    history.push(feedbackDetailsPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={feedback.unicefId}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={feedbackDetailsPath}>{feedback.unicefId}</BlackLink>
        ) : (
          feedback.unicefId
        )}
      </TableCell>
      <TableCell align='left'>
        {feedback.issueType === 'A_1'
          ? 'Positive Feedback'
          : 'Negative Feedback'}
      </TableCell>
      <TableCell align='left'>
        {feedback.householdLookup?.id ? (
          <BlackLink to={householdDetailsPath}>
            {feedback.householdLookup?.unicefId}
          </BlackLink>
        ) : (
          renderSomethingOrDash(feedback.householdLookup?.unicefId)
        )}
      </TableCell>
      <TableCell align='left'>
        {feedback.linkedGrievance?.id ? (
          <BlackLink to={grievanceDetailsPath}>
            {feedback.linkedGrievance?.unicefId}
          </BlackLink>
        ) : (
          renderSomethingOrDash(feedback.linkedGrievance?.unicefId)
        )}
      </TableCell>
      <TableCell align='left'>{renderUserName(feedback.createdBy)}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{feedback.createdAt}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};
