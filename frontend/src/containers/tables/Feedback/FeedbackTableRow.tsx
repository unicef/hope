import * as React from 'react';
import TableCell from '@mui/material/TableCell';
import { useHistory } from 'react-router-dom';
import {
  FeedbackIssueType,
  FeedbackNode,
} from '../../../__generated__/graphql';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@components/core/BlackLink';
import { renderSomethingOrDash, renderUserName } from '@utils/utils';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { getGrievanceDetailsPath } from '@components/grievances/utils/createGrievanceUtils';

interface FeedbackTableRowProps {
  feedback: FeedbackNode;
  canViewDetails: boolean;
}

export function FeedbackTableRow({
  feedback,
  canViewDetails,
}: FeedbackTableRowProps): React.ReactElement {
const navigate = useNavigate()  const { baseUrl, isAllPrograms } = useBaseUrl();
  const feedbackDetailsPath = `/${baseUrl}/grievance/feedback/${feedback.id}`;
  const householdDetailsPath = `/${baseUrl}/population/household/${feedback.householdLookup?.id}`;
  const grievanceDetailsPath = feedback.linkedGrievance
    ? getGrievanceDetailsPath(
      feedback.linkedGrievance?.id,
      feedback.linkedGrievance?.category,
      baseUrl,
    )
    : null;
  const handleClick = (): void => {
    navigate(feedbackDetailsPath);
  };

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={feedback.unicefId}
    >
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={feedbackDetailsPath}>{feedback.unicefId}</BlackLink>
        ) : (
          feedback.unicefId
        )}
      </TableCell>
      <TableCell align="left">
        {feedback.issueType === FeedbackIssueType.PositiveFeedback
          ? 'Positive Feedback'
          : 'Negative Feedback'}
      </TableCell>
      <TableCell align="left">
        {feedback.householdLookup?.id && !isAllPrograms ? (
          <BlackLink to={householdDetailsPath}>
            {feedback.householdLookup?.unicefId}
          </BlackLink>
        ) : (
          renderSomethingOrDash(feedback.householdLookup?.unicefId)
        )}
      </TableCell>
      <TableCell align="left">
        {feedback.linkedGrievance?.id ? (
          <BlackLink to={grievanceDetailsPath}>
            {feedback.linkedGrievance?.unicefId}
          </BlackLink>
        ) : (
          renderSomethingOrDash(feedback.linkedGrievance?.unicefId)
        )}
      </TableCell>
      <TableCell align="left">{renderUserName(feedback.createdBy)}</TableCell>
      <TableCell align="left">
        <UniversalMoment>{feedback.createdAt}</UniversalMoment>
      </TableCell>
      {isAllPrograms && (
        <TableCell align="left">
          {feedback.program?.id ? (
            <BlackLink
              key={feedback.program?.id}
              to={`/${baseUrl}/details/${feedback.program?.id}`}
            >
              {feedback?.program.name}
            </BlackLink>
          ) : (
            '-'
          )}
        </TableCell>
      )}
    </ClickableTableRow>
  );
}
