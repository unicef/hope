import { useGrievanceTicketUnicefIdQuery } from '@generated/graphql';
import { BlueText } from '../LookUpStyles';
import { ReactElement } from 'react';

export function LinkedTicketIdDisplay({
  ticketId,
}: {
  ticketId: string;
}): ReactElement {
  const { data } = useGrievanceTicketUnicefIdQuery({
    variables: { id: ticketId },
  });
  return (
    <BlueText data-cy="linked-ticket-id">
      {data?.grievanceTicket?.unicefId}
    </BlueText>
  );
}
