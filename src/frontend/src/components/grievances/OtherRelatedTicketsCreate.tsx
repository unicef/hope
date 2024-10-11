import { Box, Typography } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useExistingGrievanceTicketsQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { decodeIdString } from '@utils/utils';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import {
  ApproveBox,
  BlueBold,
} from './GrievancesApproveSection/ApproveSectionStyles';
import { getGrievanceDetailsPath } from './utils/createGrievanceUtils';

export function OtherRelatedTicketsCreate({ values }): React.ReactElement {
  const { t } = useTranslation();
  const { baseUrl, businessArea } = useBaseUrl();
  const [show, setShow] = useState(false);

  const { data, loading } = useExistingGrievanceTicketsQuery({
    variables: {
      businessArea,
      household:
        // TODO Janek to jeszcze kiedyś wymyśli
        decodeIdString(values?.selectedHousehold?.id) ||
        '294cfa7e-b16f-4331-8014-a22ffb2b8b3c',
      // adding some random ID to get 0 results if there is no household id.
    },
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;

  const existingTickets = data.existingGrievanceTickets.edges;
  const renderIds = (tickets): React.ReactElement =>
    tickets.length
      ? tickets.map((edge) => {
        const grievanceDetailsPath = getGrievanceDetailsPath(
          edge.node.id,
          edge.node.category,
          baseUrl,
        );
        return (
            <Box key={edge.node.id} mb={1}>
              <ContentLink href={grievanceDetailsPath}>
                {edge.node.unicefId}
              </ContentLink>
            </Box>
        );
      })
      : '-';

  const openExistingTickets = existingTickets.length
    ? existingTickets.filter(
      (edge) => edge.node.status !== GRIEVANCE_TICKET_STATES.CLOSED,
    )
    : [];
  const closedExistingTickets = existingTickets.length
    ? existingTickets.filter(
      (edge) => edge.node.status === GRIEVANCE_TICKET_STATES.CLOSED,
    )
    : [];

  return existingTickets.length ? (
    <ApproveBox>
      <Title>
        <Typography variant="h6">{t('Other Related Tickets')}</Typography>
      </Title>
      <Box display="flex" flexDirection="column">
        <LabelizedField
          label={`${t('For Household')} ${
            values?.selectedHousehold?.unicefId || '-'
          } `}
        >
          <>{renderIds(openExistingTickets)}</>
        </LabelizedField>
        {!show && closedExistingTickets.length ? (
          <Box mt={3}>
            <BlueBold onClick={() => setShow(true)}>
              {t('SHOW CLOSED TICKETS')} ({closedExistingTickets.length})
            </BlueBold>
          </Box>
        ) : null}
        {show && (
          <Box mb={3} mt={3}>
            <Typography>{t('Closed Tickets')}</Typography>
            <LabelizedField
              label={`${t('For Household')} ${
                values?.selectedHousehold?.unicefId || '-'
              } `}
            >
              <>{renderIds(closedExistingTickets)}</>
            </LabelizedField>
          </Box>
        )}
        {show && closedExistingTickets.length ? (
          <BlueBold onClick={() => setShow(false)}>
            {t('HIDE CLOSED TICKETS')} ({closedExistingTickets.length})
          </BlueBold>
        ) : null}
      </Box>
    </ApproveBox>
  ) : null;
}
