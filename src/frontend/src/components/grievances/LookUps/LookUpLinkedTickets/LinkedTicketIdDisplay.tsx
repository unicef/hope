import * as React from 'react';
import { useGrievanceTicketUnicefIdQuery } from '@generated/graphql';
import { BlueText } from '../LookUpStyles';

export function LinkedTicketIdDisplay({
  ticketId,
}: {
  ticketId: string;
}): React.ReactElement {
  const { data } = useGrievanceTicketUnicefIdQuery({
    variables: { id: ticketId },
  });
  return (
    <BlueText data-cy="linked-ticket-id">
      {data?.grievanceTicket?.unicefId}
    </BlueText>
  );
}
