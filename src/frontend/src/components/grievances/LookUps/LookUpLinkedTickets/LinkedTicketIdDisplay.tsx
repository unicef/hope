import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { BlueText } from '../LookUpStyles';
import { ReactElement } from 'react';

export function LinkedTicketIdDisplay({
  ticketId,
}: {
  ticketId: string;
}): ReactElement {
  const { businessArea } = useBaseUrl();

  const { data } = useQuery({
    queryKey: ['grievanceTicket', ticketId, businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsRetrieve({
        businessAreaSlug: businessArea,
        id: ticketId,
      }),
    enabled: !!ticketId,
  });

  return <BlueText data-cy="linked-ticket-id">{data?.unicefId}</BlueText>;
}
