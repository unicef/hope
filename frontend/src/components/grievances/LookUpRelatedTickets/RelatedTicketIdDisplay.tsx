import React from 'react';
import styled from 'styled-components';
import { useGrievanceTicketUnicefIdQuery } from '../../../__generated__/graphql';

const BlueText = styled.span`
  color: #033f91;
  font-weight: 500;
  font-size: 16px;
`;

export const RelatedTicketIdDisplay = ({
  ticketId,
}: {
  ticketId: string;
}): React.ReactElement => {
  const { data } = useGrievanceTicketUnicefIdQuery({
    variables: { id: ticketId },
  });
  return <BlueText>{data?.grievanceTicket?.unicefId}</BlueText>;
};
