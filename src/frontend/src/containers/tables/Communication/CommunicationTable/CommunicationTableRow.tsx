import TableCell from '@mui/material/TableCell';
import { useNavigate } from 'react-router-dom';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import type { MessageList } from '@restgenerated/models/MessageList';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

interface CommunicationTableRowProps {
  message: MessageList;
  canViewDetails: boolean;
}

export function CommunicationTableRow({
  message,
  canViewDetails,
}: CommunicationTableRowProps): ReactElement {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const messageDetailsPath = `/${baseUrl}/accountability/communication/${message.id}`;
  const handleClick = (): void => {
    navigate(messageDetailsPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={message.unicefId}
    >
      <TableCell align="left">
        {canViewDetails ? (
          <BlackLink to={messageDetailsPath}>{message.unicefId}</BlackLink>
        ) : (
          message.unicefId
        )}
      </TableCell>
      <TableCell align="left">{message.title}</TableCell>
      <TableCell align="left">{message.numberOfRecipients}</TableCell>
      <TableCell align="left">{message.createdBy}</TableCell>
      <TableCell align="left">
        <UniversalMoment>{message.createdAt}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
