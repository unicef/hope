import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BlackLink } from '@components/core/BlackLink';
import { renderSomethingOrDash } from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { getGrievanceDetailsPath } from '@components/grievances/utils/createGrievanceUtils';
import { ReactElement } from 'react';
import { FeedbackList } from '@restgenerated/models/FeedbackList';

interface FeedbackTableRowProps {
  feedback: FeedbackList;
  canViewDetails: boolean;
}

export function FeedbackTableRow({
  feedback,
  canViewDetails,
}: FeedbackTableRowProps): ReactElement {
  const navigate = useNavigate();
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const feedbackDetailsPath = `/${baseUrl}/grievance/feedback/${feedback.id}`;
  const householdDetailsPath = feedback.householdId
    ? `/${baseUrl}/population/household/${feedback.householdId}`
    : null;
  const grievanceDetailsPath = feedback.linkedGrievanceId
    ? getGrievanceDetailsPath(
        feedback.linkedGrievanceId,
        1, // Default to category 1 as we don't have category info in REST model
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
        {feedback.issueType === 'POSITIVE_FEEDBACK'
          ? 'Positive Feedback'
          : 'Negative Feedback'}
      </TableCell>
      <TableCell align="left">
        {feedback.householdId && !isAllPrograms ? (
          <BlackLink to={householdDetailsPath}>
            {feedback.householdUnicefId}
          </BlackLink>
        ) : (
          renderSomethingOrDash(feedback.householdUnicefId)
        )}
      </TableCell>
      <TableCell align="left">
        {feedback.linkedGrievanceId ? (
          <BlackLink to={grievanceDetailsPath}>
            {feedback.linkedGrievanceUnicefId}
          </BlackLink>
        ) : (
          renderSomethingOrDash(feedback.linkedGrievanceUnicefId)
        )}
      </TableCell>
      <TableCell align="left">{feedback.createdBy}</TableCell>
      <TableCell align="left">
        <UniversalMoment>{feedback.createdAt}</UniversalMoment>
      </TableCell>
      {isAllPrograms && (
        <TableCell align="left">
          {feedback.programId ? (
            <BlackLink
              key={feedback.programId}
              to={`/${baseUrl}/details/${feedback.programId}`}
            >
              {feedback.programName}
            </BlackLink>
          ) : (
            '-'
          )}
        </TableCell>
      )}
    </ClickableTableRow>
  );
}
