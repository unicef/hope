import { Box, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { decodeIdString } from '../../utils/utils';
import { GrievanceTicketQuery } from '../../__generated__/graphql';
import { ContentLink } from '../ContentLink';
import { LabelizedField } from '../LabelizedField';

const StyledBox = styled.div`
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
  border-radius: 3px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;
const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

const BlueBold = styled.div`
  color: ${({ theme }) => theme.hctPalette.navyBlue};
  font-weight: 500;
  cursor: pointer;
`;

export const OtherRelatedTickets = ({
  linkedTickets,
}: {
  linkedTickets: GrievanceTicketQuery['grievanceTicket']['linkedTickets']['edges'];
}) => {
  const businessArea = useBusinessArea();
  const [show, setShow] = useState(false);

  const renderIds = (tickets) =>
    tickets.map((edge) => (
      <Box mb={1}>
        <ContentLink
          href={`/${businessArea}/grievance-and-feedback/${edge.node.id}`}
        >
          {decodeIdString(edge.node.id)}
        </ContentLink>
      </Box>
    ));

  const openTickets =
    linkedTickets.length &&
    linkedTickets.filter(
      (edge) => edge.node.status !== GRIEVANCE_TICKET_STATES.CLOSED,
    );
  const closedTickets =
    linkedTickets.length &&
    linkedTickets.filter(
      (edge) => edge.node.status === GRIEVANCE_TICKET_STATES.CLOSED,
    );

  return linkedTickets.length ? (
    <StyledBox>
      <Title>
        <Typography variant='h6'>Other Related Tickets</Typography>
      </Title>
      <Box display='flex' flexDirection='column'>
        <LabelizedField label='Tickets'>
          <>{renderIds(openTickets)}</>
        </LabelizedField>
        {!show && (
          <Box mt={3}>
            <BlueBold onClick={() => setShow(true)}>
              SHOW CLOSED TICKETS ({closedTickets.length})
            </BlueBold>
          </Box>
        )}
        {show && (
          <Box mb={3} mt={3}>
            <Typography>Closed Tickets</Typography>
            <LabelizedField label='Tickets'>
              <>{renderIds(closedTickets)}</>
            </LabelizedField>
          </Box>
        )}
        {show && (
          <BlueBold onClick={() => setShow(false)}>
            HIDE CLOSED TICKETS ({closedTickets.length})
          </BlueBold>
        )}
      </Box>
    </StyledBox>
  ) : null;
};
