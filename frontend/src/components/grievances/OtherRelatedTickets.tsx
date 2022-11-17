import { Box, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { decodeIdString } from '../../utils/utils';
import {
  GrievanceTicketNode,
  useExistingGrievanceTicketsQuery,
} from '../../__generated__/graphql';
import { ContentLink } from '../core/ContentLink';
import { LabelizedField } from '../core/LabelizedField';
import { LoadingComponent } from '../core/LoadingComponent';
import { Title } from '../core/Title';
import {
  ApproveBox,
  BlueBold,
} from './GrievancesApproveSection/ApproveSectionStyles';

export const OtherRelatedTickets = ({
  linkedTickets,
  ticket,
}: {
  linkedTickets: GrievanceTicketNode['relatedTickets'];
  ticket: GrievanceTicketNode;
}): React.ReactElement => {
  const { t } = useTranslation();
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
  const renderIds = (tickets): React.ReactElement =>
    tickets.length
      ? tickets.map((edge) => (
          <Box key={edge.node.id} mb={1}>
            <ContentLink
              href={`/${businessArea}/grievance-and-feedback/${edge.node.id}`}
            >
              {edge.node.unicefId}
            </ContentLink>
          </Box>
        ))
      : '-';
  const renderRelatedIds = (tickets): React.ReactElement =>
    tickets.length
      ? tickets.map((edge) => (
          <Box key={edge.id} mb={1}>
            <ContentLink
              href={`/${businessArea}/grievance-and-feedback/${edge.id}`}
            >
              {edge.unicefId}
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
    <ApproveBox>
      <Title>
        <Typography variant='h6'>{t('Other Related Tickets')}</Typography>
      </Title>
      <Box display='flex' flexDirection='column'>
        <LabelizedField
          label={`For Household ${ticket.household?.unicefId || '-'} `}
        >
          <>{renderIds(openHouseholdTickets)}</>
        </LabelizedField>
        <LabelizedField label={t('Tickets')}>
          <>{renderRelatedIds(openTickets)}</>
        </LabelizedField>
        {!show && (closedTickets.length || closedHouseholdTickets.length) ? (
          <Box mt={3}>
            <BlueBold onClick={() => setShow(true)}>
              {t('SHOW CLOSED TICKETS')} (
              {closedTickets.length + closedHouseholdTickets.length})
            </BlueBold>
          </Box>
        ) : null}
        {show && (
          <Box mb={3} mt={3}>
            <Typography>{t('Closed Tickets')}</Typography>
            <LabelizedField
              label={`${t('For Household')} ${ticket.household?.unicefId ||
                '-'} `}
            >
              <>{renderIds(closedHouseholdTickets)}</>
            </LabelizedField>
            <LabelizedField label={t('Tickets')}>
              <>{renderRelatedIds(closedTickets)}</>
            </LabelizedField>
          </Box>
        )}
        {show && (closedTickets.length || closedHouseholdTickets.length) ? (
          <BlueBold onClick={() => setShow(false)}>
            {t('HIDE CLOSED TICKETS')} (
            {closedTickets.length + closedHouseholdTickets.length})
          </BlueBold>
        ) : null}
      </Box>
    </ApproveBox>
  ) : null;
};
