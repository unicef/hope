import React from 'react';
import { useGrievanceTicketUnicefIdQuery } from '../../../../__generated__/graphql';
import { BlueText } from '../LookUpStyles';

export const LinkedTicketIdDisplay = ({
  ticketId,
}: {
  ticketId: string;
}): React.ReactElement => {
  const { data } = useGrievanceTicketUnicefIdQuery({
    variables: { id: ticketId },
  });
  return (
    <BlueText data-cy='linked-ticket-id'>
      {data?.grievanceTicket?.unicefId}
    </BlueText>
  );
};
