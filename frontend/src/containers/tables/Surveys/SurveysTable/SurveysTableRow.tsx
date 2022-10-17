import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { BlackLink } from '../../../../components/core/BlackLink';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { renderSomethingOrDash, renderUserName } from '../../../../utils/utils';
import {
  FeedbackNode,
  FeedbackIssueType,
} from '../../../../__generated__/graphql';

interface SurveysTableRowProps {
  feedback: FeedbackNode;
  canViewDetails: boolean;
}

export const SurveysTableRow = ({
  feedback,
  canViewDetails,
}: SurveysTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const feedbackDetailsPath = `/${businessArea}/accountability/surveys/${feedback.id}`;
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
        {feedback.issueType === FeedbackIssueType.PositiveFeedback
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
