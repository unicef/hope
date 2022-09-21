import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { CommunicationMessageNode } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../components/core/UniversalMoment';
import { BlackLink } from '../../../components/core/BlackLink';
import { renderUserName } from '../../../utils/utils';

interface CommunicationTableRowProps {
  message: CommunicationMessageNode;
  canViewDetails?: boolean;
}

export function CommunicationTableRow({
  message,
  canViewDetails,
}: CommunicationTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const messageDetailsPath = `/${businessArea}/accountability/communication/${message.id}`;
  const handleClick = (): void => {
    history.push(messageDetailsPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={message.unicefId}
    >
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={messageDetailsPath}>{message.unicefId}</BlackLink>
        ) : (
          message.unicefId
        )}
      </TableCell>
      <TableCell align='left'>{message.title}</TableCell>
      <TableCell align='left'>{message.numberOfRecipients}</TableCell>
      <TableCell align='left'>{renderUserName(message.createdBy)}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{message.createdAt}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}
