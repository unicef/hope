import { Box, Paper, Typography } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import React, { useState } from 'react';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { decodeIdString } from '../../utils/utils';
import {
  GrievanceTicketQuery,
  useExistingGrievanceTicketsQuery,
} from '../../__generated__/graphql';
import { ContentLink } from '../ContentLink';
import { LabelizedField } from '../LabelizedField';
import { LoadingComponent } from '../LoadingComponent';

const StyledBox = styled(Paper)`
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
  ticket,
}: {
  linkedTickets: GrievanceTicketQuery['grievanceTicket']['relatedTickets'];
  ticket: GrievanceTicketQuery['grievanceTicket'];
}) => {
  const businessArea = useBusinessArea();
  const { id } = useParams();

  const [show, setShow] = useState(false);

  const { data, loading } = useExistingGrievanceTicketsQuery({
    variables: {
      businessArea,
      household:
        decodeIdString(ticket.household?.id) ||
        '294cfa7e-b16f-4331-8014-a22ffb2b8b3c',
      //adding some random ID to get 0 results if there is no household id.
    },
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;

  const householdTickets = data.existingGrievanceTickets.edges;
  const renderIds = (tickets) =>
    tickets.length
      ? tickets.map((edge) => (
          <Box key={edge.node.id} mb={1}>
            <ContentLink
              target='_blank'
              rel='noopener noreferrer'
              href={`/${businessArea}/grievance-and-feedback/${edge.node.id}`}
            >
              {decodeIdString(edge.node.id)}
            </ContentLink>
          </Box>
        ))
      : '-';
  const renderRelatedIds = (tickets) =>
    tickets.length
      ? tickets.map((edge) => (
          <Box key={edge.id} mb={1}>
            <ContentLink
              target='_blank'
              rel='noopener noreferrer'
              href={`/${businessArea}/grievance-and-feedback/${edge.id}`}
            >
              {decodeIdString(edge.id)}
            </ContentLink>
          </Box>
        ))
      : '-';

  const openHouseholdTickets =
    ticket.household?.id && householdTickets.length
      ? householdTickets.filter(
          (edge) =>
            edge.node.status !== GRIEVANCE_TICKET_STATES.CLOSED &&
            edge.node.id !== id,
        )
      : [];
  const closedHouseholdTickets =
    ticket.household?.id && householdTickets.length
      ? householdTickets.filter(
          (edge) =>
            edge.node.status === GRIEVANCE_TICKET_STATES.CLOSED &&
            edge.node.id !== id,
        )
      : [];

  const openTickets = linkedTickets.length
    ? linkedTickets.filter(
        (edge) =>
          edge.status !== GRIEVANCE_TICKET_STATES.CLOSED && edge.id !== id,
      )
    : [];
  const closedTickets = linkedTickets.length
    ? linkedTickets.filter(
        (edge) =>
          edge.status === GRIEVANCE_TICKET_STATES.CLOSED && edge.id !== id,
      )
    : [];

  return linkedTickets.length || householdTickets.length ? (
    <StyledBox>
      <Title>
        <Typography variant='h6'>Other Related Tickets</Typography>
      </Title>
      <Box display='flex' flexDirection='column'>
        <LabelizedField label='For Household'>
          <>{renderIds(openHouseholdTickets)}</>
        </LabelizedField>
        <LabelizedField label='Tickets'>
          <>{renderRelatedIds(openTickets)}</>
        </LabelizedField>
        {!show && (closedTickets.length || closedHouseholdTickets.length) ? (
          <Box mt={3}>
            <BlueBold onClick={() => setShow(true)}>
              SHOW CLOSED TICKETS (
              {closedTickets.length + closedHouseholdTickets.length})
            </BlueBold>
          </Box>
        ) : null}
        {show && (
          <Box mb={3} mt={3}>
            <Typography>Closed Tickets</Typography>
            <LabelizedField label='For Household'>
              <>{renderIds(closedHouseholdTickets)}</>
            </LabelizedField>
            <LabelizedField label='Tickets'>
              <>{renderRelatedIds(closedTickets)}</>
            </LabelizedField>
          </Box>
        )}
        {show && (closedTickets.length || closedHouseholdTickets.length) ? (
          <BlueBold onClick={() => setShow(false)}>
            HIDE CLOSED TICKETS (
            {closedTickets.length + closedHouseholdTickets.length})
          </BlueBold>
        ) : null}
      </Box>
    </StyledBox>
  ) : null;
};
