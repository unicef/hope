import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { BlackLink } from '@components/core/BlackLink';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { Survey } from '@restgenerated/models/Survey';

interface SurveysTableRowProps {
  survey: Survey;
  canViewDetails: boolean;
  categoryDict;
}

export function SurveysTableRow({
  survey,
  canViewDetails,
  categoryDict,
}: SurveysTableRowProps): ReactElement {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const surveyDetailsPath = `/${baseUrl}/accountability/surveys/${survey.id}`;

  const handleClick = (): void => {
    navigate(surveyDetailsPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={survey.unicefId}
    >
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={surveyDetailsPath}>{survey.unicefId}</BlackLink>
        ) : (
          survey.unicefId
        )}
      </TableCell>
      <TableCell align="left">{survey.title}</TableCell>
      <TableCell align="left">{categoryDict[survey.category]}</TableCell>
      <TableCell align="left">{survey.numberOfRecipients || 'N/A'}</TableCell>
      <TableCell align="left">{survey.createdBy}</TableCell>
      <TableCell align="left">
        <UniversalMoment>{survey.createdAt}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
