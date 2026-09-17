import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { BlueText } from '../LookUpStyles';
import type { ReactElement } from 'react';

export function LinkedTicketIdDisplay({
  ticketId,
}: {
  ticketId: string;
}): ReactElement {
  const { businessArea } = useBaseUrl();

  const { data } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasGrievanceTicketsRetrieve,
      { businessAreaSlug: businessArea, id: ticketId },
    ),
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsRetrieve({
        businessAreaSlug: businessArea,
        id: ticketId,
      }),
    enabled: !!ticketId,
  });

  return <BlueText data-cy="linked-ticket-id">{data?.unicefId}</BlueText>;
}
