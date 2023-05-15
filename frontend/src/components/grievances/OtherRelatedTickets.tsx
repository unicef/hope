import { Box, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { GrievanceTicketQuery } from '../../__generated__/graphql';
import { ContentLink } from '../core/ContentLink';
import { LabelizedField } from '../core/LabelizedField';
import { Title } from '../core/Title';
import {
  ApproveBox,
  BlueBold,
} from './GrievancesApproveSection/ApproveSectionStyles';

export const OtherRelatedTickets = ({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const { id } = useParams();

  const [show, setShow] = useState(false);
  const { existingTickets, linkedTickets } = ticket;

  const renderIds = (tickets): React.ReactElement =>
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

  const openExistingTickets =
    ticket.household?.id && existingTickets.length
      ? existingTickets.filter(
          (edge) =>
            edge.status !== GRIEVANCE_TICKET_STATES.CLOSED && edge.id !== id,
        )
      : [];
  const closedExistingTickets =
    ticket.household?.id && existingTickets.length
      ? existingTickets.filter(
          (edge) =>
            edge.status === GRIEVANCE_TICKET_STATES.CLOSED && edge.id !== id,
        )
      : [];

  const openLinkedTickets = linkedTickets.length
    ? linkedTickets.filter(
        (edge) =>
          edge.status !== GRIEVANCE_TICKET_STATES.CLOSED && edge.id !== id,
      )
    : [];
  const closedLinkedTickets = linkedTickets.length
    ? linkedTickets.filter(
        (edge) =>
          edge.status === GRIEVANCE_TICKET_STATES.CLOSED && edge.id !== id,
      )
    : [];

  return linkedTickets.length > 0 || existingTickets.length > 0 ? (
    <ApproveBox>
      <Title>
        <Typography variant='h6'>{t('Other Related Tickets')}</Typography>
      </Title>
      <Box display='flex' flexDirection='column'>
        <LabelizedField
          label={`For Household ${ticket.household?.unicefId || '-'} `}
        >
          <>{renderIds(openExistingTickets)}</>
        </LabelizedField>
        <LabelizedField label={t('Tickets')}>
          <>{renderIds(openLinkedTickets)}</>
        </LabelizedField>
        {!show &&
        (closedLinkedTickets.length > 0 || closedExistingTickets.length > 0) ? (
          <Box mt={3}>
            <BlueBold onClick={() => setShow(true)}>
              {t('SHOW CLOSED TICKETS')} (
              {closedLinkedTickets.length + closedExistingTickets.length})
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
              <>{renderIds(closedExistingTickets)}</>
            </LabelizedField>
            <LabelizedField label={t('Tickets')}>
              <>{renderIds(closedLinkedTickets)}</>
            </LabelizedField>
          </Box>
        )}
        {show &&
        (closedLinkedTickets.length > 0 || closedExistingTickets.length > 0) ? (
          <BlueBold onClick={() => setShow(false)}>
            {t('HIDE CLOSED TICKETS')} (
            {closedLinkedTickets.length + closedExistingTickets.length})
          </BlueBold>
        ) : null}
      </Box>
    </ApproveBox>
  ) : null;
};
