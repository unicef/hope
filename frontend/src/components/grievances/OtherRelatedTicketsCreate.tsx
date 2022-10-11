import { Box, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { decodeIdString } from '../../utils/utils';
import { useExistingGrievanceTicketsQuery } from '../../__generated__/graphql';
import { ContentLink } from '../core/ContentLink';
import { LabelizedField } from '../core/LabelizedField';
import { LoadingComponent } from '../core/LoadingComponent';
import { Title } from '../core/Title';
import {
  ApproveBox,
  BlueBold,
} from './GrievancesApproveSection/ApproveSectionStyles';

export function OtherRelatedTicketsCreate({ values }): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const [show, setShow] = useState(false);

  const { data, loading } = useExistingGrievanceTicketsQuery({
    variables: {
      businessArea,
      household:
        //TODO Janek to jeszcze kiedyś wymyśli
        decodeIdString(values?.selectedHousehold?.id) ||
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

  const openHouseholdTickets = householdTickets.length
    ? householdTickets.filter(
        (edge) => edge.node.status !== GRIEVANCE_TICKET_STATES.CLOSED,
      )
    : [];
  const closedHouseholdTickets = householdTickets.length
    ? householdTickets.filter(
        (edge) => edge.node.status === GRIEVANCE_TICKET_STATES.CLOSED,
      )
    : [];

  const shouldShowBox = values.category && values.selectedHousehold?.id;

  return shouldShowBox && householdTickets.length ? (
    <ApproveBox>
      <Title>
        <Typography variant='h6'>{t('Other Related Tickets')}</Typography>
      </Title>
      <Box display='flex' flexDirection='column'>
        <LabelizedField
          label={`${t('For Household')} ${values?.selectedHousehold?.unicefId ||
            '-'} `}
        >
          <>{renderIds(openHouseholdTickets)}</>
        </LabelizedField>
        {!show && closedHouseholdTickets.length ? (
          <Box mt={3}>
            <BlueBold onClick={() => setShow(true)}>
              {t('SHOW CLOSED TICKETS')} ({closedHouseholdTickets.length})
            </BlueBold>
          </Box>
        ) : null}
        {show && (
          <Box mb={3} mt={3}>
            <Typography>{t('Closed Tickets')}</Typography>
            <LabelizedField
              label={`${t('For Household')} ${values?.selectedHousehold
                ?.unicefId || '-'} `}
            >
              <>{renderIds(closedHouseholdTickets)}</>
            </LabelizedField>
          </Box>
        )}
        {show && closedHouseholdTickets.length ? (
          <BlueBold onClick={() => setShow(false)}>
            {t('HIDE CLOSED TICKETS')} ({closedHouseholdTickets.length})
          </BlueBold>
        ) : null}
      </Box>
    </ApproveBox>
  ) : null;
}
